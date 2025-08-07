import logging
from importlib import import_module
from typing import Any, Collection
logger = logging.getLogger(__name__)
try:
    from fi.evals import Protect
except ImportError:
    logger.warning("ai-evaluation is not installed, please install it to trace protect")
    Protect = None
    pass
from fi_instrumentation import FITracer, TraceConfig
from fi_instrumentation.instrumentation._protect_wrapper import GuardrailProtectWrapper
from groq.resources.chat.completions import AsyncCompletions, Completions
from opentelemetry import trace as trace_api
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor  # type: ignore
from traceai_groq._wrappers import _AsyncCompletionsWrapper, _CompletionsWrapper
from traceai_groq.version import __version__
from wrapt import wrap_function_wrapper

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_instruments = ("groq >= 0.9.0",)


class GroqInstrumentor(BaseInstrumentor):  # type: ignore[misc]
    """An instrumentor for the Groq framework."""

    __slots__ = (
        "_original_completions_create",
        "_original_async_completions_create",
        "_tracer",
    )

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs: Any) -> None:
        if not (tracer_provider := kwargs.get("tracer_provider")):
            tracer_provider = trace_api.get_tracer_provider()
        if not (config := kwargs.get("config")):
            config = TraceConfig()
        else:
            assert isinstance(config, TraceConfig)
        self._tracer = FITracer(
            trace_api.get_tracer(__name__, __version__, tracer_provider),
            config=config,
        )

        self._original_completions_create = Completions.create
        wrap_function_wrapper(
            module="groq.resources.chat.completions",
            name="Completions.create",
            wrapper=_CompletionsWrapper(tracer=self._tracer),
        )

        self._original_async_completions_create = AsyncCompletions.create
        wrap_function_wrapper(
            module="groq.resources.chat.completions",
            name="AsyncCompletions.create",
            wrapper=_AsyncCompletionsWrapper(tracer=self._tracer),
        )

        if Protect is not None:
            self._original_protect = Protect.protect
            wrap_function_wrapper(
                module="fi.evals",
                name="Protect.protect",
                wrapper=GuardrailProtectWrapper(tracer=self._tracer),
            )

    def _uninstrument(self, **kwargs: Any) -> None:
        groq_module = import_module("groq.resources.chat.completions")
        if self._original_completions_create is not None:
            groq_module.Completions.create = self._original_completions_create
        if self._original_async_completions_create is not None:
            groq_module.AsyncCompletions.create = (
                self._original_async_completions_create
            )
