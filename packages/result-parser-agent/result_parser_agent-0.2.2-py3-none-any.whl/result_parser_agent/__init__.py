"""Results Parser Agent - A deep agent for extracting metrics from result files."""

from .agent.parser_agent import ResultsParserAgent
from .config.settings import (
    DEFAULT_CONFIG,
    AgentConfig,
    LLMConfig,
    ParserConfig,
    ParsingConfig,
)
from .config.utils import (
    create_config,
    get_anthropic_config,
    get_google_config,
    get_groq_config,
    get_ollama_config,
    get_openai_config,
    load_config_from_file,
    modify_config,
    save_config_to_file,
)

__version__ = "0.2.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "ResultsParserAgent",
    "ParserConfig",
    "AgentConfig",
    "LLMConfig",
    "ParsingConfig",
    "DEFAULT_CONFIG",
    # Configuration utilities
    "create_config",
    "load_config_from_file",
    "save_config_to_file",
    "modify_config",
    "get_groq_config",
    "get_openai_config",
    "get_anthropic_config",
    "get_google_config",
    "get_ollama_config",
]
