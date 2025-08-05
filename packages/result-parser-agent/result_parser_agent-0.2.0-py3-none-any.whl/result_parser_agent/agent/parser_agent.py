from typing import Annotated, Any, TypedDict

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from loguru import logger

from ..config.settings import ParserConfig
from ..models.schema import StructuredResults
from ..prompts.agent_prompts import get_initial_message, get_system_prompt
from ..tools.langchain_tools import create_tools


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "The messages in the conversation"]
    remaining_steps: Annotated[int, "Number of remaining steps"]
    todos: Annotated[list[str], "List of tasks to complete"]
    files: Annotated[dict[str, Any], "Discovered files and their info"]
    parsing_progress: Annotated[dict[str, Any], "Progress tracking for each file"]
    extracted_data: Annotated[dict[str, Any], "Extracted metrics data"]
    raw_context: Annotated[dict[str, str], "Filepath to raw context mapping"]
    errors: Annotated[list[str], "List of errors encountered"]
    config: Annotated[Any, "Configuration object"]
    context: Annotated[dict[str, Any], "Context information"]


class ResultsParserAgent:
    def __init__(self, config: ParserConfig):
        self.config = config
        self.model = self._create_llm_model()
        self.agent = self._create_agent()
        self.structured_llm = self.model.with_structured_output(StructuredResults)

    def _create_llm_model(self) -> LanguageModelLike:
        llm_config = self.config.get_llm_config()
        provider = llm_config["provider"]

        if provider == "groq":
            from langchain_groq import ChatGroq

            return ChatGroq(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
            )
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model_name=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
            )
        elif provider == "ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=llm_config["model"], temperature=float(llm_config["temperature"])
            )
        elif provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=llm_config["model"],
                api_key=llm_config["api_key"],
                temperature=float(llm_config["temperature"]),
                max_output_tokens=(
                    int(llm_config["max_tokens"]) if llm_config["max_tokens"] else None
                ),
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    def _create_agent(self) -> Any:
        from langgraph.prebuilt import create_react_agent

        tools = create_tools(None)
        return create_react_agent(self.model, tools, debug=self.config.agent.debug)

    def _get_system_prompt(self) -> str:
        return get_system_prompt(self.config.parsing.metrics)

    async def parse_results(
        self, input_path: str, metrics: list[str] | None = None
    ) -> StructuredResults:
        try:
            logger.info(f"Starting autonomous parsing of: {input_path}")
            target_metrics = metrics or self.config.parsing.metrics

            initial_messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=get_initial_message(input_path, target_metrics)),
            ]

            if self.config.agent.debug:
                logger.info("🔍 Initial messages created.")
                logger.debug(
                    f"System prompt length: {len(initial_messages[0].content)}"
                )
                logger.debug(
                    f"Human message length: {len(initial_messages[1].content)}"
                )

            runnable_config = RunnableConfig(recursion_limit=50)
            result = await self.agent.ainvoke(
                {"messages": initial_messages}, config=runnable_config
            )

            final_agent_message = result["messages"][-1]
            if not hasattr(final_agent_message, "content"):
                raise ValueError("Final agent message has no content.")

            structured_result = await self.structured_llm.ainvoke(
                final_agent_message.content
            )

            if self.config.agent.debug:
                logger.info("✅ Structured result successfully parsed.")
                logger.debug(f"{structured_result}")

            return structured_result

        except Exception as e:
            logger.error(f"❌ Error in parse_results: {e}")
            if self.config.agent.debug:
                import traceback

                logger.error(traceback.format_exc())

            return StructuredResults(iterations=[])
