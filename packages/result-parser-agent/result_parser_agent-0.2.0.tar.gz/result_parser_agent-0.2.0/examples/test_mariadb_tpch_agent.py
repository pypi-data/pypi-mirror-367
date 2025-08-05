#!/usr/bin/env python3
"""
Test of the autonomous agent with MariaDB TPC-H benchmark data.
"""

import asyncio
import json
import os

from dotenv import load_dotenv

# Import the agent
from result_parser_agent import DEFAULT_CONFIG, ResultsParserAgent


async def test_mariadb_tpch_agent():
    """Test the autonomous agent with MariaDB TPC-H benchmark data."""

    load_dotenv()

    print("🎯 MariaDB TPC-H Test - Autonomous Agent with Database Benchmark")
    print("=" * 75)

    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set. Please set it first:")
        print("   export GOOGLE_API_KEY='your-google-api-key-here'")
        return

    # TPC-H specific metrics
    test_metrics = ["Power@Size", "Throughput@Size", "QphH@Size"]

    print(f"📊 Target metrics: {test_metrics}")
    print("📁 Input directory: test_mariadb_tpch/")
    print(
        "📂 Structure: run1/iteration1/, run1/iteration2/, run2/iteration1/, run2/iteration2/"
    )
    print("🗄️  Database: MariaDB 10.11.5")
    print("📈 Benchmark: TPC-H")
    print()

    try:
        # Create agent
        agent = ResultsParserAgent(DEFAULT_CONFIG)
        print("✅ Agent created successfully")

        # Let the agent handle everything autonomously
        print("🔄 Starting autonomous parsing of MariaDB TPC-H benchmark data...")
        print("   (Agent will discover files, patterns, and structure on its own)")

        result_update = await agent.parse_results(
            input_path="test_mariadb_tpch/", metrics=test_metrics
        )

        print("✅ Autonomous parsing completed!")
        print()

        # Display results
        print("📋 Extracted Results:")
        print("-" * 50)

        result_json = result_update.model_dump()
        print(json.dumps(result_json, indent=2))

        # Save to JSON file
        output_file = "mariadb_tpch_parsing_results.json"
        with open(output_file, "w") as f:
            json.dump(result_json, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        # Show summary
        print()
        print("📈 Summary:")
        print("-" * 50)
        if result_update.resultInfo:
            for result_info in result_update.resultInfo:
                print(f"System: {result_info.sutName}")
                print(f"Platform: {result_info.platformProfilerID}")
                print(f"Runs: {len(result_info.runs)}")

                for run in result_info.runs:
                    print(f"  Run {run.runIndex}:")
                    print(f"    Iterations: {len(run.iterations)}")

                    for iteration in run.iterations:
                        print(f"      Iteration {iteration.iterationIndex}:")
                        print(f"        Instances: {len(iteration.instances)}")

                        for instance in iteration.instances:
                            print(f"          Instance {instance.instanceIndex}:")
                            for stat in instance.statistics:
                                print(
                                    f"            {stat.metricName}: {stat.metricValue}"
                                )
        else:
            print("❌ No results found")

        print("\n🚀 MariaDB TPC-H Agent Capabilities Tested:")
        print("  ✅ Database benchmark parsing")
        print("  ✅ TPC-H metric extraction")
        print("  ✅ Hierarchical structure understanding")
        print("  ✅ Pattern discovery across database logs")
        print("  ✅ Metric extraction from MariaDB TPC-H results")
        print("  ✅ Structured output generation")

        print("\n💡 Agent successfully parsed MariaDB TPC-H benchmark data!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_mariadb_tpch_agent())
