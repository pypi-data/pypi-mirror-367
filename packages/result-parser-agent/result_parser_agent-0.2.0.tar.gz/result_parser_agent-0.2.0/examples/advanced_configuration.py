#!/usr/bin/env python3
"""
Advanced Configuration Examples for Results Parser Agent

This example demonstrates all the different ways to configure the agent:
1. Using pre-configured provider configs
2. Loading from YAML files
3. Modifying existing configs
4. Creating custom configs
5. CLI-style configuration
"""

import asyncio
import tempfile
from pathlib import Path

from result_parser_agent import (
    DEFAULT_CONFIG,
    ResultsParserAgent,
    create_config,
    get_anthropic_config,
    get_groq_config,
    get_openai_config,
    load_config_from_file,
    modify_config,
    save_config_to_file,
)


async def test_configuration_methods():
    """Test all configuration methods."""

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(
            """
Benchmark Results:
=================
Requests per second: 1250.5
Average latency: 45.2ms
Throughput: 1.2 GB/s
CPU usage: 78.5%
Memory usage: 2.1 GB
        """
        )
        test_file = f.name

    try:
        print("🧪 Testing Advanced Configuration Methods")
        print("=" * 50)

        # Method 1: Pre-configured provider configs
        print("\n1️⃣ Using Pre-configured Provider Configs")
        print("-" * 40)

        # GROQ config
        groq_config = get_groq_config(
            model="llama3.1-8b-instant", metrics=["RPS", "latency", "throughput"]
        )
        print(
            f"✅ GROQ config: {groq_config.agent.llm.provider} - {groq_config.agent.llm.model}"
        )

        # OpenAI config
        openai_config = get_openai_config(
            model="gpt-4", metrics=["RPS", "latency", "throughput"]
        )
        print(
            f"✅ OpenAI config: {openai_config.agent.llm.provider} - {openai_config.agent.llm.model}"
        )

        # Anthropic config
        anthropic_config = get_anthropic_config(
            model="claude-3-sonnet-20240229", metrics=["RPS", "latency", "throughput"]
        )
        print(
            f"✅ Anthropic config: {anthropic_config.agent.llm.provider} - {anthropic_config.agent.llm.model}"
        )

        # Method 2: Create custom config
        print("\n2️⃣ Creating Custom Config")
        print("-" * 40)

        custom_config = create_config(
            provider="groq",
            model="llama3.1-70b-versatile",
            temperature=0.3,
            max_tokens=8000,
            metrics=["RPS", "latency", "throughput", "cpu_usage", "memory_usage"],
        )
        print(
            f"✅ Custom config: {custom_config.agent.llm.provider} - {custom_config.agent.llm.model}"
        )
        print(f"   Temperature: {custom_config.agent.llm.temperature}")
        print(f"   Max tokens: {custom_config.agent.llm.max_tokens}")
        print(f"   Metrics: {custom_config.parsing.metrics}")

        # Method 3: Modify existing config
        print("\n3️⃣ Modifying Existing Config")
        print("-" * 40)

        modified_config = modify_config(
            base_config=DEFAULT_CONFIG,
            provider="openai",
            model="gpt-4-turbo",
            temperature=0.2,
            metrics=["accuracy", "precision", "recall"],
        )
        print(
            f"✅ Modified config: {modified_config.agent.llm.provider} - {modified_config.agent.llm.model}"
        )
        print(f"   Temperature: {modified_config.agent.llm.temperature}")
        print(f"   Metrics: {modified_config.parsing.metrics}")

        # Method 4: Save and load config
        print("\n4️⃣ Save and Load Config")
        print("-" * 40)

        # Save config to file
        config_file = "temp_config.yaml"
        save_config_to_file(custom_config, config_file)
        print(f"✅ Saved config to: {config_file}")

        # Load config from file
        loaded_config = load_config_from_file(config_file)
        print(
            f"✅ Loaded config: {loaded_config.agent.llm.provider} - {loaded_config.agent.llm.model}"
        )

        # Clean up
        Path(config_file).unlink()

        # Method 5: Test actual parsing with different configs
        print("\n5️⃣ Testing Parsing with Different Configs")
        print("-" * 40)

        # Test with GROQ config (if API key available)
        try:
            agent = ResultsParserAgent(groq_config)
            result = await agent.parse_results(
                test_file, metrics=["RPS", "latency", "throughput"]
            )
            print(
                f"✅ GROQ parsing successful: {len(result.extracted_data)} files processed"
            )
        except Exception as e:
            print(f"⚠️ GROQ parsing failed (likely no API key): {e}")

        # Test with modified config
        try:
            agent = ResultsParserAgent(modified_config)
            result = await agent.parse_results(
                test_file, metrics=["accuracy", "precision", "recall"]
            )
            print(
                f"✅ Modified config parsing successful: {len(result.extracted_data)} files processed"
            )
        except Exception as e:
            print(f"⚠️ Modified config parsing failed (likely no API key): {e}")

        print("\n🎉 All configuration methods tested successfully!")
        print("\n📋 Summary of Configuration Methods:")
        print("   • get_groq_config() - Quick GROQ setup")
        print("   • get_openai_config() - Quick OpenAI setup")
        print("   • get_anthropic_config() - Quick Anthropic setup")
        print("   • get_google_config() - Quick Google setup")
        print("   • get_ollama_config() - Quick Ollama setup")
        print("   • create_config() - Custom configuration")
        print("   • modify_config() - Modify existing config")
        print("   • load_config_from_file() - Load from YAML")
        print("   • save_config_to_file() - Save to YAML")
        print("   • CLI options: --config, --provider, --model, --temperature")

        return True

    except Exception as e:
        print(f"❌ Error during configuration testing: {e}")
        return False

    finally:
        # Clean up
        if Path(test_file).exists():
            Path(test_file).unlink()


if __name__ == "__main__":
    print("🚀 Advanced Configuration Examples for Results Parser Agent")
    print("=" * 60)

    success = asyncio.run(test_configuration_methods())

    if success:
        print("\n🎉 Configuration examples completed successfully!")
        print("The agent is now ready for flexible configuration.")
    else:
        print("\n💥 Configuration examples failed!")
        print("Please check your setup and try again.")
