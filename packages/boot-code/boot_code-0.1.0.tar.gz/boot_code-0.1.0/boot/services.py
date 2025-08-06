# FILE: boot/services.py
"""
Orchestrates the entire project generation lifecycle, including an optional,
recursive build-and-fix loop with detailed pass-by-pass logging.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import List

from boot.core.file_packager import PackedFile, pack_from_raw
from boot.core.plugin_manager import PluginManager
from boot.core.prompt_engine import PromptEngine
from boot.core.writer import ProjectWriter
from boot.generated import plugin_pb2
from boot.llm.service import LLMService
from boot.llm.types import GenerationConfig
from boot.models.config import AppSettings
from boot.models.spec import SpexSpecification
from boot.parsers.factory import create_parser
from boot.ui.console import ConsoleManager
from boot.utils.helpers import get_timestamp, slugify


class GeneratorService:
    """
    Orchestrates the project generation process with a multi-pass workflow.
    This service is responsible for the entire lifecycle, from spec validation
    to final file output, including an iterative build-and-fix loop.
    """

    def __init__(self, settings: AppSettings):
        """
        Initializes the service and its dependencies.

        Args:
            settings: The application settings, which control generation behavior.
        """
        self.settings = settings
        self.project_writer = ProjectWriter()
        self.prompt_engine = PromptEngine()
        self.llm_service = LLMService(settings)
        self._pass_counter = 0
        self._log_dir: Path | None = None

    def _create_output_directory(self, spec: SpexSpecification) -> Path:
        """
        Creates a unique, timestamped directory for the generated project and its logs.

        Args:
            spec: The user's validated specification.

        Returns:
            The path to the newly created project root directory.
        """
        timestamp = get_timestamp()
        project_slug = slugify(spec.project.name)
        project_dir_name = f"{timestamp}__{project_slug}"

        output_dir = self.settings.output_dir / spec.language.lower() / project_dir_name
        self._log_dir = output_dir / "_boot_logs"
        self._log_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    async def _run_llm_pass(
        self, prompt: str, manager: ConsoleManager, pass_name: str
    ) -> tuple[str, list[PackedFile]]:
        """
        Executes a single pass of interaction with the LLM.

        This function sends a prompt to the LLM, receives the raw text response,
        parses it into a list of files, and logs all artifacts for debugging.

        Args:
            prompt: The complete prompt to send to the LLM.
            manager: The console manager for displaying progress.
            pass_name: A descriptive name for the current pass (e.g., "Initial Generation").

        Returns:
            A tuple containing the raw text response and the list of parsed files.
        """
        self._pass_counter += 1
        pass_num = self._pass_counter

        manager.start_step(f"Running LLM pass: {pass_name} (Pass #{pass_num})")
        config = GenerationConfig(
            prompt=prompt,
            model=self.settings.get_model(),
            temperature=self.settings.temperature or 0.1,
            timeout_s=self.settings.http_timeout_seconds,
        )
        raw_text = (await self.llm_service.generate(config)).text
        manager.complete_step()

        files, _ = pack_from_raw(raw_text)

        if self._log_dir:
            log_file = self._log_dir / f"raw_llm_output_pass_{pass_num}.txt"
            log_file.write_text(raw_text, "utf-8")
            self.project_writer.write_interim_files(self._log_dir, pass_num, files)

        return raw_text, files

    async def _run_build_and_fix_loop(
        self,
        files: list[PackedFile],
        spec: SpexSpecification,
        output_dir: Path,
        manager: ConsoleManager,
    ) -> list[PackedFile]:
        """
        Manages the iterative process of building the code, parsing errors,
        and prompting the LLM to fix them.

        Args:
            files: The initial set of generated files.
            spec: The user's specification.
            output_dir: The directory where the project is being built.
            manager: The console manager for UI updates.

        Returns:
            The final, successfully built list of files.
        """
        error_parser = create_parser(spec.language)

        for attempt in range(self.settings.max_fix_attempts):
            manager.start_step(
                f"Attempting to build project (Attempt {attempt + 1}/{self.settings.max_fix_attempts})"
            )
            self.project_writer.write_project_files(output_dir, files)

            try:
                process = subprocess.run(
                    ["make", "build"],
                    cwd=output_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )

                if self._log_dir:
                    build_log_file = (
                        self._log_dir / f"raw_build_output_attempt_{attempt + 1}.log"
                    )
                    build_log_file.write_text(
                        process.stdout + "\n" + process.stderr, "utf-8"
                    )

                if process.returncode == 0:
                    manager.complete_step("Build successful!")
                    return files
                else:
                    manager.fail_step()
                    manager.print_warning("Build failed. Attempting to fix...")
                    error_output = process.stderr or process.stdout
                    parsed_errors = error_parser.parse(error_output)

                    if self._log_dir:
                        parsed_log_file = (
                            self._log_dir
                            / f"parsed_build_errors_attempt_{attempt + 1}.log"
                        )
                        parsed_log_file.write_text(parsed_errors, "utf-8")

                    fix_prompt = self.prompt_engine.build_fix_prompt(
                        original_files=files,
                        build_errors=parsed_errors,
                    )
                    _, files = await self._run_llm_pass(
                        fix_prompt, manager, f"Code Fix Attempt {attempt + 1}"
                    )

            except FileNotFoundError:
                manager.print_error(
                    "'make' command not found. Please ensure it's installed and in your PATH."
                )
                break
            except Exception as e:
                manager.print_error(
                    f"An unexpected error occurred during the build: {e}"
                )
                break

        manager.print_warning(
            "Max build attempts reached. Using the last generated version."
        )
        return files

    async def generate_from_spec(
        self, spec_path: Path, manager: ConsoleManager
    ) -> Path:
        """
        The main orchestration method for the entire generation workflow.
        """
        manager.start_step("Validating specification")
        spec = SpexSpecification.from_toml(spec_path)
        output_dir = self._create_output_directory(spec)
        manager.print_info(f"Project directory created at: {output_dir}")

        with open(spec_path, "r", encoding="utf-8") as f:
            spec_content = f.read()

        plugin_name = f"boot-{spec.language.lower()}"
        plugin_manager = PluginManager(plugin_name)
        prompt_map = {}
        user_spec_prompt = ""
        scaffolding_files: List[PackedFile] = []
        plugin_found = False

        try:
            manager.start_step(f"Looking for '{plugin_name}' plugin...")
            plugin_manager.start()
            plugin_found = True
            manager.complete_step(f"Plugin '{plugin_name}' found and initialized.")

            manager.start_step(f"Fetching prompt components from '{plugin_name}'")
            # Ignore mypy error for dynamically generated gRPC attribute
            prompt_req = plugin_pb2.GetPromptComponentsRequest(  # type: ignore[attr-defined]
                spec_toml_content=spec_content
            )
            # Ignore mypy error for attribute on a potentially None object
            # (although start() would have raised if it were None)
            if plugin_manager.client_stub:
                prompt_components = await asyncio.to_thread(
                    plugin_manager.client_stub.GetPromptComponents, prompt_req
                )
                manager.complete_step()
                prompt_map = {k: v for k, v in prompt_components.components.items()}
                user_spec_prompt = prompt_components.user_spec_prompt

                if "Makefile" in prompt_map:
                    makefile_content = prompt_map.pop("Makefile")
                    scaffolding_files.append(
                        PackedFile(path="Makefile", content=makefile_content)
                    )

        except FileNotFoundError:
            manager.fail_step(f"Plugin '{plugin_name}' not found.")
            manager.print_warning("Falling back to generic generation mode.")
            prompt_map["base_instructions.txt"] = """
You are an expert-level code generator.
Your task is to write a complete, robust, and idiomatic application based on the user's specifications provided in the TOML file below.

CRITICAL RULES:
- You MUST NOT write any conversational text, explanations, or apologies.
- You MUST generate a complete and runnable implementation for every file required for the project, including a Makefile for building and running the project.
- You MUST format the entire response as a series of markdown code blocks, each preceded by a `### FILE: <path>` marker.
"""
            prompt_map["language_rules.txt"] = ""
            user_spec_prompt = f"--- USER SPECIFICATION (TOML) ---\n{spec_content}"

        finally:
            if plugin_found:
                plugin_manager.stop()

        initial_prompt = self.prompt_engine.build_generate_prompt(
            base_instructions=prompt_map.get("base_instructions.txt", ""),
            language_rules=prompt_map.get("language_rules.txt", ""),
            user_spec_prompt=user_spec_prompt,
        )
        raw_text, llm_files = await self._run_llm_pass(
            initial_prompt, manager, "Initial Code Generation"
        )

        final_files = llm_files + scaffolding_files

        if self.settings.build_pass and final_files:
            final_files = await self._run_build_and_fix_loop(
                final_files, spec, output_dir, manager
            )

        if self.settings.two_pass and final_files:
            review_prompt = self.prompt_engine.build_review_prompt(
                initial_code=raw_text,
                review_instructions_template=prompt_map.get(
                    "review_instructions.txt", ""
                ),
                language_rules=prompt_map.get("language_rules.txt", ""),
                user_spec_prompt=user_spec_prompt,
            )
            _, llm_files = await self._run_llm_pass(
                review_prompt, manager, "Final Review Pass"
            )
            final_files = llm_files + scaffolding_files

        manager.start_step("Writing final project files")
        self.project_writer.write_project_files(output_dir, final_files)
        manager.complete_step()
        return output_dir
