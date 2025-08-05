#!/usr/bin/env python3
"""
Test script to verify GROQ support in the Results Parser Agent.
"""

import asyncio
import os
import tempfile

from result_parser_agent import (
    AgentConfig,
    LLMConfig,
    ParserConfig,
    ParsingConfig,
    ResultsParserAgent,
)


async def test_groq_support():
    """Test GROQ support with a simple configuration."""

    # Check if GROQ API key is set
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set it with: export GROQ_API_KEY='your-api-key-here'")
        return False

    print("✅ GROQ API key found")

    # Create a GROQ-specific configuration
    config = ParserConfig(
        agent=AgentConfig(
            llm=LLMConfig(
                provider="groq",
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                api_key=groq_api_key,
            )
        ),
        parsing=ParsingConfig(metrics=["RPS", "latency", "throughput"]),
    )

    print("✅ Configuration created with GROQ provider")

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(
            """
Benchmark Results:
=================
Requests per second: 1250.5
Average latency: 45.2ms
Throughput: 1.2 GB/s
        """
        )
        test_file = f.name

    try:
        print("✅ Test file created")

        # Initialize the agent
        agent = ResultsParserAgent(config)
        print("✅ ResultsParserAgent initialized with GROQ")

        # Test parsing
        print("🔄 Testing parsing with GROQ...")
        result = await agent.parse_results(
            test_file, metrics=["RPS", "latency", "throughput"]
        )

        print("✅ Parsing completed successfully!")
        print(f"📊 Extracted data: {result.extracted_data}")

        return True

    except Exception as e:
        print(f"❌ Error during GROQ test: {e}")
        return False

    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)


if __name__ == "__main__":
    print("🧪 Testing GROQ Support for Results Parser Agent")
    print("=" * 50)

    success = asyncio.run(test_groq_support())

    if success:
        print("\n🎉 GROQ support test PASSED!")
        print("The agent is ready to use with GROQ.")
    else:
        print("\n💥 GROQ support test FAILED!")
        print("Please check your configuration and API key.")
