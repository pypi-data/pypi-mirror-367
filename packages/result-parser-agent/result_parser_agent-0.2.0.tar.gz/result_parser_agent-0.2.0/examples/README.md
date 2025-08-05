# Examples

This directory contains examples demonstrating how to use the Results Parser Agent.

## 🚀 Quick Start with GROQ (Recommended)

GROQ provides fast, reliable LLM inference that's perfect for parsing tasks:

```bash
# Set your GROQ API key
export GROQ_API_KEY="your-groq-api-key-here"

# Test GROQ support
uv run python examples/test_groq_support.py

# Use with GROQ configuration
result-parser --config examples/configs/groq_config.yaml --file your_results.txt
```

## Available Examples

### `test_hierarchical_agent.py`
Demonstrates the autonomous agent parsing hierarchical folder structures with multiple runs, iterations, and instances. This is the main example showing the agent's capabilities.

### `test_final_parsing.py`
Shows how to use the agent for parsing individual result files and extracting specific metrics.

### `advanced_configuration.py`
Comprehensive example demonstrating all configuration methods:
- Pre-configured provider configs (GROQ, OpenAI, Anthropic, etc.)
- Loading from YAML files
- Modifying existing configs
- Creating custom configs
- CLI-style configuration

## Configuration

### `configs/parser_config.yaml`
Example configuration file showing how to configure the agent with different LLM providers and parsing settings.

### `configs/groq_config.yaml`
GROQ-specific configuration optimized for fast parsing tasks with the `llama3.1-8b-instant` model.

## Sample Data

### `sample_results/`
Contains sample result files for testing the agent.

## Usage

```bash
# Test hierarchical parsing
uv run examples/test_hierarchical_agent.py

# Test single file parsing
uv run examples/test_final_parsing.py

# Test advanced configuration methods
uv run examples/advanced_configuration.py
```

Make sure to set your `GROQ_API_KEY` environment variable before running the examples (recommended), or use another provider like `GOOGLE_API_KEY`. 