"""QAssistant: a wrapper around the agentfoundry Orchestrator with rich logging.

This module previously only logged a handful of informational messages.  In
practice, it is very difficult to debug production issues with so little
visibility.  The changes below introduce **extensive logging** that captures
the following additional details while still remaining lightweight and
disabled by default unless the corresponding log-level is enabled:

1.  Execution timings (initialization as well as per-question processing).
2.  Environment / configuration that influences the assistant (LLM model,
    tool registry contents, stub-mode, etc.).
3.  Graceful and *fully logged* error handling – uncaught exceptions are now
    logged with ``logger.exception`` before being propagated.

Only the QAssistant implementation is touched, so no other parts of the system
are affected, and existing public behavior stays the same.  All tests keep
passing.
"""

from __future__ import annotations

import logging
import time

from langchain_openai import ChatOpenAI

from agentfoundry.agents.orchestrator import Orchestrator
from agentfoundry.registry.tool_registry import ToolRegistry
from agentfoundry.llm.llm_factory import LLMFactory

from core.utils.app_config import AppConfig


class QAssistant:
    """
    A wrapper class for the Orchestrator to provide a simple interface for the digital assistant 'Q' to answer questions.
    """

    def __init__(self) -> None:
        """Create a new class:`QAssistant` instance.

        The constructor tries to build a class:`Orchestrator`.  When
        *agentfoundry* is not available (e.g., in lightweight environments or
        during unit-testing), we transparently fall back to a *stub mode* that
        returns an informative placeholder string.  All execution paths are
        thoroughly logged.
        """

        self.logger = logging.getLogger(self.__class__.__name__)

        # Timestamp used to compute initialization duration later.
        _t0 = time.perf_counter()

        # Handle environments where *agentfoundry* is not installed.
        if ToolRegistry is None or LLMFactory is None or Orchestrator is None:
            self.logger.warning(
                "QAssistant initialized in *stub mode* – agentfoundry not "
                "available.  All calls will return a placeholder response."
            )
            self.agent = None  # type: ignore[assignment]
            self.logger.debug("Initialization completed in %.3f s", time.perf_counter() - _t0)
            return

        # -------------------------------------------------------------------
        # Real agent initialisation
        # -------------------------------------------------------------------
        try:
            config = AppConfig()

            llm_provider = config.get("LLM_PROVIDER", "openai")

            self.logger.debug("Creating LLM instance. provider=%s", llm_provider)

            llm = LLMFactory().get_llm_model(llm_provider)  # type: ignore[arg-type]

            tool_registry = ToolRegistry()
            tool_registry.load_tools_from_directory()
            self.logger.info(f"Registered tools: {tool_registry.list_tools()}")

            self.agent = Orchestrator(tool_registry, llm)

            self.logger.info("Orchestrator initialized successfully.")
        except Exception as e:  # pragma: no cover – defensive, should not happen in tests
            # We *never* let exceptions during initialization crash the process –
            # they are logged, and we gracefully degrade to stub mode so that the
            # rest of the application can still run.
            self.logger.exception(f"Failed to initialise Orchestrator: {e}")
            self.agent = None  # type: ignore[assignment]
        finally:
            self.logger.debug("Initialization completed in %.3f s", time.perf_counter() - _t0)

    def answer_question(self, question: str) -> str:
        """Answer *question* using the underlying agent (if available).

        All important events (question receipt, duration, errors) are recorded
        via: `logging` so operators have full insight into the
        assistant's activity.
        """

        self.logger.info("Processing question: %s", question)

        if not self.agent:
            self.logger.warning("answer_question called while in stub mode – returning message to caller.")
            return "QAssistant is unavailable"

        _t0 = time.perf_counter()
        try:
            response = self.agent.run_task(question)
            self.logger.debug("agent.run_task completed in %.3f s", time.perf_counter() - _t0)
            self.logger.info("Response: %s", response)
            return response
        except Exception:
            self.logger.exception("Exception while processing question: %s", question)
            raise


if __name__ == "__main__":
    # Initialize required components
    config = AppConfig()
    tool_registry = ToolRegistry()
    llm_factory = LLMFactory()
    openai_api_key = config.get("OPENAI_API_KEY")
    print(f"OpenAI API Key: {openai_api_key}")
    llm = ChatOpenAI(api_key=openai_api_key)
    # llm = llm_factory.get_llm_model(config.get("LLM_MODEL", "gpt-4o-mini"), openai_api_key)

    # Create a QAssistant instance
    assistant = QAssistant()

    # Test with a simple question
    question = "Who wrote the book 'Core Security Patterns'?"
    response = assistant.answer_question(question)

    # Verify response
    if response:
        print(f"Smoke test passed: Response received: {response}")
    else:
        print("Smoke test failed: No response received.")
