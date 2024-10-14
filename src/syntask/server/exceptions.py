from syntask.exceptions import SyntaskException


class ObjectNotFoundError(SyntaskException):
    """
    Error raised by the Syntask REST API when a requested object is not found.

    If thrown during a request, this exception will be caught and
    a 404 response will be returned.
    """


class OrchestrationError(SyntaskException):
    """An error raised while orchestrating a state transition"""


class MissingVariableError(SyntaskException):
    """An error raised by the Syntask REST API when attempting to create or update a
    deployment with missing required variables.
    """


class FlowRunGraphTooLarge(Exception):
    """Raised to indicate that a flow run's graph has more nodes that the configured
    maximum"""
