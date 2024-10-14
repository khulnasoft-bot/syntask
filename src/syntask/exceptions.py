"""
Syntask-specific exceptions.
"""

import inspect
import traceback
from types import ModuleType, TracebackType
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type

from httpx._exceptions import HTTPStatusError
from pydantic import ValidationError
from rich.traceback import Traceback
from typing_extensions import Self

import syntask


def _trim_traceback(
    tb: TracebackType, remove_modules: Iterable[ModuleType]
) -> Optional[TracebackType]:
    """
    Utility to remove frames from specific modules from a traceback.

    Only frames from the front of the traceback are removed. Once a traceback frame
    is reached that does not originate from `remove_modules`, it is returned.

    Args:
        tb: The traceback to trim.
        remove_modules: An iterable of module objects to remove.

    Returns:
        A traceback, or `None` if all traceback frames originate from an excluded module

    """
    strip_paths = [module.__file__ for module in remove_modules]

    while tb and any(
        module_path in str(tb.tb_frame.f_globals.get("__file__", ""))
        for module_path in strip_paths
    ):
        tb = tb.tb_next

    return tb


def exception_traceback(exc: Exception) -> str:
    """
    Convert an exception to a printable string with a traceback
    """
    tb = traceback.TracebackException.from_exception(exc)
    return "".join(list(tb.format()))


class SyntaskException(Exception):
    """
    Base exception type for Syntask errors.
    """


class CrashedRun(SyntaskException):
    """
    Raised when the result from a crashed run is retrieved.

    This occurs when a string is attached to the state instead of an exception or if
    the state's data is null.
    """


class FailedRun(SyntaskException):
    """
    Raised when the result from a failed run is retrieved and an exception is not
    attached.

    This occurs when a string is attached to the state instead of an exception or if
    the state's data is null.
    """


class CancelledRun(SyntaskException):
    """
    Raised when the result from a cancelled run is retrieved and an exception
    is not attached.

    This occurs when a string is attached to the state instead of an exception
    or if the state's data is null.
    """


class PausedRun(SyntaskException):
    """
    Raised when the result from a paused run is retrieved.
    """

    def __init__(self, *args, state=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state


class UnfinishedRun(SyntaskException):
    """
    Raised when the result from a run that is not finished is retrieved.

    For example, if a run is in a SCHEDULED, PENDING, CANCELLING, or RUNNING state.
    """


class MissingFlowError(SyntaskException):
    """
    Raised when a given flow name is not found in the expected script.
    """


class UnspecifiedFlowError(SyntaskException):
    """
    Raised when multiple flows are found in the expected script and no name is given.
    """


class MissingResult(SyntaskException):
    """
    Raised when a result is missing from a state; often when result persistence is
    disabled and the state is retrieved from the API.
    """


class ScriptError(SyntaskException):
    """
    Raised when a script errors during evaluation while attempting to load data
    """

    def __init__(
        self,
        user_exc: Exception,
        path: str,
    ) -> None:
        message = f"Script at {str(path)!r} encountered an exception: {user_exc!r}"
        super().__init__(message)
        self.user_exc = user_exc

        # Strip script run information from the traceback
        self.user_exc.__traceback__ = _trim_traceback(
            self.user_exc.__traceback__,
            remove_modules=[syntask.utilities.importtools],
        )


class FlowScriptError(SyntaskException):
    """
    Raised when a script errors during evaluation while attempting to load a flow.
    """

    def __init__(
        self,
        user_exc: Exception,
        script_path: str,
    ) -> None:
        message = f"Flow script at {script_path!r} encountered an exception"
        super().__init__(message)

        self.user_exc = user_exc

    def rich_user_traceback(self, **kwargs):
        trace = Traceback.extract(
            type(self.user_exc),
            self.user_exc,
            self.user_exc.__traceback__.tb_next.tb_next.tb_next.tb_next,
        )
        return Traceback(trace, **kwargs)


class ParameterTypeError(SyntaskException):
    """
    Raised when a parameter does not pass Pydantic type validation.
    """

    def __init__(self, msg: str):
        super().__init__(msg)

    @classmethod
    def from_validation_error(cls, exc: ValidationError) -> Self:
        bad_params = [
            f'{".".join(str(item) for item in err["loc"])}: {err["msg"]}'
            for err in exc.errors()
        ]
        msg = "Flow run received invalid parameters:\n - " + "\n - ".join(bad_params)
        return cls(msg)


class ParameterBindError(TypeError, SyntaskException):
    """
    Raised when args and kwargs cannot be converted to parameters.
    """

    def __init__(self, msg: str):
        super().__init__(msg)

    @classmethod
    def from_bind_failure(
        cls, fn: Callable, exc: TypeError, call_args: List, call_kwargs: Dict
    ) -> Self:
        fn_signature = str(inspect.signature(fn)).strip("()")

        base = f"Error binding parameters for function '{fn.__name__}': {exc}"
        signature = f"Function '{fn.__name__}' has signature '{fn_signature}'"
        received = f"received args: {call_args} and kwargs: {list(call_kwargs.keys())}"
        msg = f"{base}.\n{signature} but {received}."
        return cls(msg)


class SignatureMismatchError(SyntaskException, TypeError):
    """Raised when parameters passed to a function do not match its signature."""

    def __init__(self, msg: str):
        super().__init__(msg)

    @classmethod
    def from_bad_params(cls, expected_params: List[str], provided_params: List[str]):
        msg = (
            f"Function expects parameters {expected_params} but was provided with"
            f" parameters {provided_params}"
        )
        return cls(msg)


class ObjectNotFound(SyntaskException):
    """
    Raised when the client receives a 404 (not found) from the API.
    """

    def __init__(
        self,
        http_exc: Exception,
        help_message: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.http_exc = http_exc
        self.help_message = help_message
        super().__init__(help_message, *args, **kwargs)

    def __str__(self):
        return self.help_message or super().__str__()


class ObjectAlreadyExists(SyntaskException):
    """
    Raised when the client receives a 409 (conflict) from the API.
    """

    def __init__(self, http_exc: Exception, *args, **kwargs):
        self.http_exc = http_exc
        super().__init__(*args, **kwargs)


class UpstreamTaskError(SyntaskException):
    """
    Raised when a task relies on the result of another task but that task is not
    'COMPLETE'
    """


class MissingContextError(SyntaskException, RuntimeError):
    """
    Raised when a method is called that requires a task or flow run context to be
    active but one cannot be found.
    """


class MissingProfileError(SyntaskException, ValueError):
    """
    Raised when a profile name does not exist.
    """


class ReservedArgumentError(SyntaskException, TypeError):
    """
    Raised when a function used with Syntask has an argument with a name that is
    reserved for a Syntask feature
    """


class InvalidNameError(SyntaskException, ValueError):
    """
    Raised when a name contains characters that are not permitted.
    """


class SyntaskSignal(BaseException):
    """
    Base type for signal-like exceptions that should never be caught by users.
    """


class Abort(SyntaskSignal):
    """
    Raised when the API sends an 'ABORT' instruction during state proposal.

    Indicates that the run should exit immediately.
    """


class Pause(SyntaskSignal):
    """
    Raised when a flow run is PAUSED and needs to exit for resubmission.
    """

    def __init__(self, *args, state=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = state


class ExternalSignal(BaseException):
    """
    Base type for external signal-like exceptions that should never be caught by users.
    """


class TerminationSignal(ExternalSignal):
    """
    Raised when a flow run receives a termination signal.
    """

    def __init__(self, signal: int):
        self.signal = signal


class SyntaskHTTPStatusError(HTTPStatusError):
    """
    Raised when client receives a `Response` that contains an HTTPStatusError.

    Used to include API error details in the error messages that the client provides users.
    """

    @classmethod
    def from_httpx_error(cls: Type[Self], httpx_error: HTTPStatusError) -> Self:
        """
        Generate a `SyntaskHTTPStatusError` from an `httpx.HTTPStatusError`.
        """
        try:
            details = httpx_error.response.json()
        except Exception:
            details = None

        error_message, *more_info = str(httpx_error).split("\n")

        if details:
            message_components = [error_message, f"Response: {details}", *more_info]
        else:
            message_components = [error_message, *more_info]

        new_message = "\n".join(message_components)

        return cls(
            new_message, request=httpx_error.request, response=httpx_error.response
        )


class MappingLengthMismatch(SyntaskException):
    """
    Raised when attempting to call Task.map with arguments of different lengths.
    """


class MappingMissingIterable(SyntaskException):
    """
    Raised when attempting to call Task.map with all static arguments
    """


class BlockMissingCapabilities(SyntaskException):
    """
    Raised when a block does not have required capabilities for a given operation.
    """


class ProtectedBlockError(SyntaskException):
    """
    Raised when an operation is prevented due to block protection.
    """


class InvalidRepositoryURLError(SyntaskException):
    """Raised when an incorrect URL is provided to a GitHub filesystem block."""


class InfrastructureError(SyntaskException):
    """
    A base class for exceptions related to infrastructure blocks
    """


class InfrastructureNotFound(SyntaskException):
    """
    Raised when infrastructure is missing, likely because it has exited or been
    deleted.
    """


class InfrastructureNotAvailable(SyntaskException):
    """
    Raised when infrastructure is not accessible from the current machine. For example,
    if a process was spawned on another machine it cannot be managed.
    """


class NotPausedError(SyntaskException):
    """Raised when attempting to unpause a run that isn't paused."""


class FlowPauseTimeout(SyntaskException):
    """Raised when a flow pause times out"""


class FlowRunWaitTimeout(SyntaskException):
    """Raised when a flow run takes longer than a given timeout"""


class SyntaskImportError(ImportError):
    """
    An error raised when a Syntask object cannot be imported due to a move or removal.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class SerializationError(SyntaskException):
    """
    Raised when an object cannot be serialized.
    """


class ConfigurationError(SyntaskException):
    """
    Raised when a configuration is invalid.
    """


class ProfileSettingsValidationError(SyntaskException):
    """
    Raised when a profile settings are invalid.
    """

    def __init__(self, errors: List[Tuple[Any, ValidationError]]) -> None:
        self.errors = errors
