import logging
from typing import Any, Callable, Collection
logger = logging.getLogger(__name__)
import haystack
try:
    from fi.evals import Protect
except ImportError:
    logger.warning("ai-evaluation is not installed, please install it to trace protect")
    Protect = None
    pass
from fi_instrumentation import FITracer, TraceConfig
from fi_instrumentation.instrumentation._protect_wrapper import GuardrailProtectWrapper
from opentelemetry import trace as trace_api
from opentelemetry.instrumentation.instrumentor import (
    BaseInstrumentor,
)  # type: ignore[attr-defined]
from traceai_haystack._wrappers import (
    _ComponentRunWrapper,
    _PipelineRunComponentWrapper,
    _PipelineWrapper,
)
from traceai_haystack.version import __version__
from wrapt import wrap_function_wrapper

logger = logging.getLogger(__name__)

_instruments = ("haystack-ai >= 2.9.0",)


class HaystackInstrumentor(BaseInstrumentor):  # type: ignore[misc]
    """An instrumentor for the Haystack framework."""

    __slots__ = (
        "_original_pipeline_run",
        "_original_pipeline_run_component",
        "_original_component_run_methods",
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

        self._original_pipeline_run = haystack.Pipeline.run
        wrap_function_wrapper(
            module="haystack.core.pipeline.pipeline",
            name="Pipeline.run",
            wrapper=_PipelineWrapper(tracer=self._tracer),
        )
        self._original_pipeline_run_component = haystack.Pipeline._run_component
        self._original_component_run_methods: dict[type[Any], Callable[..., Any]] = {}

        def wrap_component_run_method(
            component_cls: type[Any], run_method: Callable[..., Any]
        ) -> None:
            if component_cls not in self._original_component_run_methods:
                self._original_component_run_methods[component_cls] = run_method
                wrap_function_wrapper(
                    module=component_cls.__module__,
                    name=f"{component_cls.__name__}.run",
                    wrapper=_ComponentRunWrapper(tracer=self._tracer),
                )

        wrap_function_wrapper(
            module="haystack.core.pipeline.pipeline",
            name="Pipeline._run_component",
            wrapper=_PipelineRunComponentWrapper(
                tracer=self._tracer, wrap_component_run_method=wrap_component_run_method
            ),
        )

        if Protect is not None:
            self._original_protect = Protect.protect
            wrap_function_wrapper(
                module="fi.evals",
                name="Protect.protect",
                wrapper=GuardrailProtectWrapper(tracer=self._tracer),
            )

    def _uninstrument(self, **kwargs: Any) -> None:

        if self._original_pipeline_run is not None:
            haystack.Pipeline.run = self._original_pipeline_run

        if self._original_pipeline_run_component is not None:
            haystack.Pipeline._run_component = self._original_pipeline_run_component

        for (
            component_cls,
            original_run_method,
        ) in self._original_component_run_methods.items():
            component_cls.run = original_run_method
