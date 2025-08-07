from importlib import import_module
from typing import Any, Collection
import logging
logger = logging.getLogger(__name__)
try:
    from fi.evals import Protect
except ImportError:
    logger.warning("ai-evaluation is not installed, please install it to trace protect")
    Protect = None
    pass
from fi_instrumentation import FITracer, TraceConfig
from fi_instrumentation.instrumentation._protect_wrapper import GuardrailProtectWrapper
from opentelemetry import trace as trace_api
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor  # type: ignore
from traceai_instructor._wrappers import _HandleResponseWrapper, _PatchWrapper
from traceai_instructor.version import __version__
from wrapt import wrap_function_wrapper

_instruments = ("instructor >= 0.0.1",)


class InstructorInstrumentor(BaseInstrumentor):  # type: ignore
    __slots__ = (
        "_tracer",
        "_original_handle_response_model",
        "_original_patch",
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

        self._original_patch = getattr(import_module("instructor"), "patch", None)
        patch_wrapper = _PatchWrapper(tracer=self._tracer)
        wrap_function_wrapper("instructor", "patch", patch_wrapper)

        self._original_handle_response_model = getattr(
            import_module("instructor.patch"), "handle_response_model", None
        )
        process_resp_wrapper = _HandleResponseWrapper(tracer=self._tracer)
        wrap_function_wrapper(
            "instructor.patch", "handle_response_model", process_resp_wrapper
        )

        if Protect is not None:
            self._original_protect = Protect.protect
            wrap_function_wrapper(
                module="fi.evals",
                name="Protect.protect",
                wrapper=GuardrailProtectWrapper(tracer=self._tracer),
            )

    def _uninstrument(self, **kwargs: Any) -> None:
        if self._original_patch is not None:
            instructor_module = import_module("instructor")
            instructor_module.patch = self._original_patch  # type: ignore[attr-defined]
            self._original_patch = None

        if self._original_handle_response_model is not None:
            patch_module = import_module("instructor.patch")
            patch_module.handle_response_model = self._original_handle_response_model  # type: ignore[attr-defined]
            self._original_handle_response_model = None
