# FILE: boot/core/prompt_engine.py
"""
Generic prompt assembly engine for the Spex application.
"""

from __future__ import annotations
from .file_packager import PackedFile


class PromptEngine:
    """Assembles final LLM prompts from externally provided components."""

    def build_generate_prompt(
        self,
        base_instructions: str,
        language_rules: str,
        user_spec_prompt: str,
    ) -> str:
        """
        Constructs the prompt for the initial code generation pass.

        Args:
            base_instructions: Core instructions for the LLM.
            language_rules: Rules specific to the target language.
            user_spec_prompt: The user's specification, formatted for the prompt.

        Returns:
            A single string representing the complete generation prompt.
        """
        prompt_parts = [
            base_instructions,
            language_rules,
            user_spec_prompt,
        ]
        return "\n\n---\n\n".join(part for part in prompt_parts if part)

    def build_review_prompt(
        self,
        initial_code: str,
        review_instructions_template: str,
        language_rules: str,
        user_spec_prompt: str,
    ) -> str:
        """
        Constructs the prompt for the secondary code review and refinement pass.

        Args:
            initial_code: The complete code generated in the first pass.
            review_instructions_template: The template for review instructions.
            language_rules: Rules specific to the target language.
            user_spec_prompt: The user's original specification.

        Returns:
            A single string representing the complete review prompt.
        """
        filled_review_instructions = review_instructions_template.format(
            initial_code=initial_code
        )
        prompt_parts = [
            filled_review_instructions,
            language_rules,
            user_spec_prompt,
        ]
        return "\n\n---\n\n".join(part for part in prompt_parts if part)

    def _format_files_for_prompt(self, files: list[PackedFile]) -> str:
        """
        Formats a list of file objects into a single string block suitable for
        inclusion in a prompt. Each file is wrapped in a markdown code block
        preceded by a `### FILE:` marker.

        Args:
            files: A list of PackedFile objects.

        Returns:
            A formatted string containing the content of all files.
        """
        return "\n".join([f"### FILE: {f.path}\n```\n{f.content}\n```" for f in files])

    def build_fix_prompt(
        self,
        original_files: list[PackedFile],
        build_errors: str,
    ) -> str:
        """
        Creates a detailed prompt that instructs the LLM to fix code based on
        compiler or build errors, providing the original code.

        Args:
            original_files: The list of files that failed to build.
            build_errors: The captured error log from the build attempt.

        Returns:
            A string representing the complete code-fixing prompt.
        """
        code_str = self._format_files_for_prompt(original_files)

        fix_it_template = f"""
You are an expert-level software engineer and debugger.
Your previous attempt to generate a project resulted in the following compiler errors.
Analyze the provided source code and the build errors.
Provide a corrected, complete version of all files to fix the issue.

**CRITICAL RULES:**
- You MUST fix the errors. The goal is to make the project build successfully.
- If the error is a dependency or version issue, you MUST correct the relevant configuration file (e.g., `Cargo.toml`, `pyproject.toml`).
- You MUST provide the complete, corrected code for ALL project files, not just the ones with errors.
- The output format must be a series of markdown code blocks, each preceded by a `### FILE: <path>` marker.

---

**COMPILER ERRORS:**
```
{build_errors}
```

---

**ORIGINAL SOURCE CODE:**
{code_str}
"""
        return fix_it_template
