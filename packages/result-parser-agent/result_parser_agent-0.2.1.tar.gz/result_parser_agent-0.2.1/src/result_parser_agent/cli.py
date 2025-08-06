"""Command-line interface for the Results Parser Agent."""

import asyncio
import json
import sys
from pathlib import Path

import typer
from loguru import logger

from .agent.parser_agent import ResultsParserAgent
from .config.settings import DEFAULT_CONFIG, ParserConfig
from .models.schema import StructuredResults


def setup_logging(verbose: bool, log_level: str = "INFO") -> None:
    """Setup logging configuration."""
    # Remove default handler
    logger.remove()

    # Add console handler
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    if verbose:
        log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}"

    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)


def validate_input_path(input_path: str) -> Path:
    """Validate and return input path."""
    path = Path(input_path)
    if not path.exists():
        raise typer.BadParameter(f"Input path does not exist: {input_path}")
    return path


def validate_metrics(metrics: list[str]) -> list[str]:
    """Validate metrics list."""
    if not metrics:
        raise typer.BadParameter("At least one metric must be specified")
    return [metric.strip() for metric in metrics]


def load_config(
    config_file: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    metrics: list[str] | None = None,
) -> ParserConfig:
    """Load and modify configuration from file or command line options."""

    # Load base configuration
    if config_file:
        config_path = Path(config_file)
        if not config_path.exists():
            raise typer.BadParameter(f"Configuration file not found: {config_file}")
        config = ParserConfig.from_yaml(config_path)
        logger.info(f"Loaded configuration from: {config_file}")
    else:
        config = DEFAULT_CONFIG
        logger.info("Using default configuration")

    # Override with command line options
    if provider:
        config.agent.llm.provider = provider
        logger.info(f"Overriding provider to: {provider}")

    if model:
        config.agent.llm.model = model
        logger.info(f"Overriding model to: {model}")

    if temperature is not None:
        config.agent.llm.temperature = temperature
        logger.info(f"Overriding temperature to: {temperature}")

    if metrics:
        config.parsing.metrics = metrics
        logger.info(f"Overriding metrics to: {metrics}")

    return config


def save_output(
    results: StructuredResults, output_path: str, pretty_print: bool = True
) -> None:
    """Save results to output file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        if pretty_print:
            json.dump(results.model_dump(), f, indent=2)
        else:
            json.dump(results.model_dump(), f)

    logger.info(f"Results saved to: {output_file}")


app = typer.Typer(
    name="result-parser",
    help="Results Parser Agent - Extract metrics from raw result files",
    add_completion=False,
)


@app.command()
def main(
    input_dir: str | None = typer.Option(
        None, "--dir", "-d", help="Directory containing result files to parse"
    ),
    input_file: str | None = typer.Option(
        None, "--file", "-f", help="Single result file to parse"
    ),
    metrics: str = typer.Option(
        ...,
        "--metrics",
        "-m",
        help="Comma-separated list of metrics to extract (required, e.g., 'RPS,latency,throughput')",
    ),
    config_file: str | None = typer.Option(
        None, "--config", "-c", help="YAML configuration file path"
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="LLM provider (groq, openai, anthropic, google, ollama)",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help="LLM model name (e.g., llama3.1-8b-instant, gpt-4, claude-3-sonnet)",
    ),
    temperature: float | None = typer.Option(
        None, "--temperature", help="LLM temperature (0.0 to 1.0)"
    ),
    output: str = typer.Option(
        "results.json",
        "--output",
        "-o",
        help="Output JSON file path (default: results.json)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Logging level", case_sensitive=False
    ),
    pretty_print: bool = typer.Option(
        True, "--pretty-print", help="Pretty print JSON output (default: True)"
    ),
    no_pretty_print: bool = typer.Option(
        False, "--no-pretty-print", help="Disable pretty printing"
    ),
) -> None:
    """
    Results Parser Agent - Extract metrics from raw result files.

    This tool intelligently parses result files and extracts specified metrics
    into structured JSON output. It supports various file formats and can handle
    large, unstructured result files.

    Examples:

        # Parse all files in a directory with default GROQ configuration
        result-parser --dir ./benchmark_results --metrics "RPS,latency" --output results.json

        # Parse a single file with custom configuration
        result-parser --file ./specific_result.txt --metrics "accuracy,precision" --provider openai --model gpt-4

        # Use a YAML configuration file
        result-parser --config ./my_config.yaml --file ./results.txt --metrics "RPS,throughput"

        # Override specific settings
        result-parser --dir ./results --metrics "RPS" --provider groq --model llama3.1-70b-versatile --temperature 0.2

        # Verbose output
        result-parser --dir ./results --metrics "RPS" --verbose
    """
    try:
        # Setup logging
        setup_logging(verbose, log_level)

        # Validate input - must provide exactly one of --dir or --file
        if not input_dir and not input_file:
            raise typer.BadParameter("Either --dir or --file must be specified")

        if input_dir and input_file:
            raise typer.BadParameter(
                "Cannot specify both --dir and --file. Use either --dir for directory or --file for single file."
            )

        # Validate metrics
        metrics_list = validate_metrics([m.strip() for m in metrics.split(",")])

        # Handle pretty print flag
        if no_pretty_print:
            pretty_print = False

        # Determine input path
        input_path = input_file if input_file else input_dir
        if input_path is None:
            raise typer.BadParameter("Input path cannot be None")
        validate_input_path(input_path)

        # Load and modify configuration
        config_obj = load_config(
            config_file=config_file,
            provider=provider,
            model=model,
            temperature=temperature,
            metrics=metrics_list,
        )

        logger.info(
            f"Starting parsing with {len(metrics_list)} metrics: {', '.join(metrics_list)}"
        )
        logger.info(f"Input path: {input_path}")
        logger.info(f"Output file: {output}")
        logger.info(f"Using provider: {config_obj.agent.llm.provider}")
        logger.info(f"Using model: {config_obj.agent.llm.model}")

        # Run the agent
        async def run_agent() -> StructuredResults:
            agent = ResultsParserAgent(config_obj)
            results = await agent.parse_results(
                input_path=input_path, metrics=metrics_list
            )
            return results

        # Execute async function
        results = asyncio.run(run_agent())

        # Save results to file
        save_output(results, output, pretty_print)

        logger.info("Parsing completed successfully")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            logger.exception("Full traceback:")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
