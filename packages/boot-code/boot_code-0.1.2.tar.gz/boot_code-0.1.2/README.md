[![CI](https://github.com/renbytes/boot-code/actions/workflows/ci.yml/badge.svg)](https://github.com/renbytes/boot-code/actions)

![Logo](docs/boot_logo.png)

👋 **Welcome to Boot\!**

**Your AI-powered code generator.**
**Write a 5-line spec. Get a working code base that passes tests and builds.**

Boot uses AI to generate production-ready code from simple specifications. No more boilerplate. No more setup hassle. Just describe what you want.

-----

### Install (30 seconds)
 
You'll need **Python 3.11 or newer**.

#### Step 1: Install the CLI

```bash
pip install boot-code
```

#### Step 2: Set your API keys

`boot` needs an API key from either [OpenAI](https://openai.com/api/) and/or [Google Gemini](https://ai.google.dev/gemini-api/docs).

The simplest way is to create a `.env` file in the project directory where you plan to run the command.

```bash
# Copy the .env file
cp .env.example .env

# Put your API keys inside .env
OPENAI_API_KEY="sk-..."
GEMINI_API_KEY="AIza..."
```

-----

### **Use (2 minutes)**

Run the main CLI module and follow the prompts:

```bash
# Generate a new pipeline from your spec
boot generate path/to/your/spec.toml

# See all available commands and options
boot --help
```

That's it. Answer a few questions, and watch your pipeline appear.

-----

### **What You Get**

  * **Complete project structure** with all the files you need.
  * **Working code** that's ready to run on your data.
  * **Unit tests** to ensure quality and reliability.
  * **Visualizations** to help you see your results.
  * **Documentation** so your team understands the pipeline.

-----

## **Why Boot?**

Instead of spending **hours writing boilerplate**, Boot generates:

✅ **Production-ready code** following best practices  
✅ **Complete test suites** with 90%+ coverage  
✅ **Interactive visualizations** for immediate insights  
✅ **Professional documentation** your team will love  
✅ **Modern tooling** (Streamlit, Black, pytest)

### **Performance Comparison**

| Metric | Manual Coding | With Boot |
|--------|---------------|-----------|
| Time to MVP | 4-8 hours | 2 minutes |
| Lines of code | 200-500 | Generated |
| Test coverage | ~60% | 90%+ |
| Documentation | Minimal | Complete |

-----

#### Advanced Usage

Below is an example of more advanced usage, using all available flags:

```bash
boot generate examples/consumer_tech/spec.toml \
--provider gemini \ 
--model gemini-2.5-pro \
--api-key "AIzaSy..." \
--two-pass \
--temperature 0.1 \
--timeout 180 \
--output-dir Desktop/ecommerce_gemini_pro
```

poetry run boot generate examples/rust/my_rust_spec.toml --build-pass

Where:
* `--provider`: Explicitly selects the LLM provider, overriding any default or `.env` setting.
* `--model`: Specifies a particular model to use for the generation, rather than the default.
* `--api-key`: Provides the API key directly on the command line, which takes precedence over any key in an `.env` file or other environment settings.
* `--two-pass`: Enables the secondary review pass, where the initial code is sent back to the LLM for refinement and improvement
* `--temperature`: Sets the generation temperature to a very low value, making the output more deterministic and less random.
* `--timeout`: Sets the API request timeout, which is useful for complex specifications that may take the model longer to process.
* `--output-dir`: Specifies a custom directory for the generated project files, overriding the default `generated_jobs` location.

### **Examples**

Explore real-world use cases in the `examples/` directory:

  * **[E-commerce](https://www.google.com/search?q=examples/ecommerce/)** - Top selling products analysis (SQL)
  * **[Healthcare](https://www.google.com/search?q=examples/healthcare/)** - Patient length of stay analysis (SQL)
  * **[Finance](https://www.google.com/search?q=examples/finance/)** - Stock volatility calculation (Python)
  * **[Energy](https://www.google.com/search?q=examples/energy/)** - Renewable energy production analysis (Python)
  * **[Consumer Tech](https://www.google.com/search?q=examples/consumer_tech/)** - Ad attribution pipeline (PySpark)

-----

### **Supported Languages**

| Language  | Framework | Use Case                        |
| :-------- | :-------- | :------------------------------ |
| **Python** | pandas    | Data analysis, reporting        |
| **PySpark** | Spark     | Big data, distributed computing |
| **SQL** | dbt-style | Data warehousing, analytics     |

-----

### **Development**

See the [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

-----

### **Support**

  * 📖 **Documentation:** Check the `docs/` directory.
  * 🐛 **Issues:** Report bugs on [GitHub Issues](https://github.com/renbytes/boot-code/issues).
