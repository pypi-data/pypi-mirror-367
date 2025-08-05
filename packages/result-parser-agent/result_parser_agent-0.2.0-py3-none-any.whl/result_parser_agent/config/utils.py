"""Configuration utilities for easy runtime configuration management."""

import os
from pathlib import Path
from typing import Any

from .settings import (
    DEFAULT_CONFIG,
    AgentConfig,
    LLMConfig,
    ParserConfig,
    ParsingConfig,
)


def create_config(
    provider: str = "groq",
    model: str = "llama3.1-8b-instant",
    api_key: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 4000,
    metrics: list[str] | None = None,
    **kwargs: Any,
) -> ParserConfig:
    """
    Create a configuration with custom settings.

    Args:
        provider: LLM provider (groq, openai, anthropic, google, ollama)
        model: LLM model name
        api_key: API key (if None, will use environment variable)
        temperature: LLM temperature (0.0 to 1.0)
        max_tokens: Maximum tokens for responses
        metrics: List of metrics to extract
        **kwargs: Additional configuration overrides

    Returns:
        ParserConfig instance
    """
    # Set default metrics if not provided
    if metrics is None:
        metrics = ["RPS", "latency", "throughput"]

    # Create LLM configuration
    llm_config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Create agent configuration
    agent_config = AgentConfig(llm=llm_config)

    # Create parsing configuration
    parsing_config = ParsingConfig(metrics=metrics)

    # Create main configuration
    config = ParserConfig(agent=agent_config, parsing=parsing_config, **kwargs)

    return config


def load_config_from_file(config_path: str | Path) -> ParserConfig:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file

    Returns:
        ParserConfig instance
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    return ParserConfig.from_yaml(config_path)


def save_config_to_file(config: ParserConfig, config_path: str | Path) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: ParserConfig instance to save
        config_path: Path to save the configuration file
    """
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config.to_yaml(config_path)


def modify_config(
    base_config: ParserConfig | None = None,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    metrics: list[str] | None = None,
    **kwargs: Any,
) -> ParserConfig:
    """
    Modify an existing configuration with new settings.

    Args:
        base_config: Base configuration to modify (uses DEFAULT_CONFIG if None)
        provider: New LLM provider
        model: New LLM model
        api_key: New API key
        temperature: New temperature
        max_tokens: New max tokens
        metrics: New metrics list
        **kwargs: Additional configuration overrides

    Returns:
        Modified ParserConfig instance
    """
    if base_config is None:
        config = DEFAULT_CONFIG
    else:
        config = base_config

    # Create a copy to avoid modifying the original
    config_dict = config.model_dump()

    # Update LLM settings
    if provider:
        config_dict["agent"]["llm"]["provider"] = provider
    if model:
        config_dict["agent"]["llm"]["model"] = model
    if api_key:
        config_dict["agent"]["llm"]["api_key"] = api_key
    if temperature is not None:
        config_dict["agent"]["llm"]["temperature"] = temperature
    if max_tokens is not None:
        config_dict["agent"]["llm"]["max_tokens"] = max_tokens

    # Update parsing settings
    if metrics:
        config_dict["parsing"]["metrics"] = metrics

    # Update other settings
    for key, value in kwargs.items():
        if key in config_dict:
            config_dict[key] = value

    return ParserConfig(**config_dict)


def get_groq_config(
    model: str = "llama3.1-8b-instant",
    api_key: str | None = None,
    metrics: list[str] | None = None,
) -> ParserConfig:
    """
    Create a GROQ-specific configuration.

    Args:
        model: GROQ model name
        api_key: GROQ API key (if None, uses GROQ_API_KEY environment variable)
        metrics: List of metrics to extract

    Returns:
        ParserConfig instance configured for GROQ
    """
    return create_config(
        provider="groq",
        model=model,
        api_key=api_key or os.getenv("GROQ_API_KEY"),
        metrics=metrics,
    )


def get_openai_config(
    model: str = "gpt-4",
    api_key: str | None = None,
    metrics: list[str] | None = None,
) -> ParserConfig:
    """
    Create an OpenAI-specific configuration.

    Args:
        model: OpenAI model name
        api_key: OpenAI API key (if None, uses OPENAI_API_KEY environment variable)
        metrics: List of metrics to extract

    Returns:
        ParserConfig instance configured for OpenAI
    """
    return create_config(
        provider="openai",
        model=model,
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        metrics=metrics,
    )


def get_anthropic_config(
    model: str = "claude-3-sonnet-20240229",
    api_key: str | None = None,
    metrics: list[str] | None = None,
) -> ParserConfig:
    """
    Create an Anthropic-specific configuration.

    Args:
        model: Anthropic model name
        api_key: Anthropic API key (if None, uses ANTHROPIC_API_KEY environment variable)
        metrics: List of metrics to extract

    Returns:
        ParserConfig instance configured for Anthropic
    """
    return create_config(
        provider="anthropic",
        model=model,
        api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
        metrics=metrics,
    )


def get_google_config(
    model: str = "gemini-2.0-flash",
    api_key: str | None = None,
    metrics: list[str] | None = None,
) -> ParserConfig:
    """
    Create a Google-specific configuration.

    Args:
        model: Google model name
        api_key: Google API key (if None, uses GOOGLE_API_KEY environment variable)
        metrics: List of metrics to extract

    Returns:
        ParserConfig instance configured for Google
    """
    return create_config(
        provider="google",
        model=model,
        api_key=api_key or os.getenv("GOOGLE_API_KEY"),
        metrics=metrics,
    )


def get_ollama_config(
    model: str = "llama3.1:8b",
    metrics: list[str] | None = None,
) -> ParserConfig:
    """
    Create an Ollama-specific configuration.

    Args:
        model: Ollama model name
        metrics: List of metrics to extract

    Returns:
        ParserConfig instance configured for Ollama
    """
    return create_config(
        provider="ollama",
        model=model,
        api_key=None,  # Ollama doesn't need API key
        metrics=metrics,
    )
