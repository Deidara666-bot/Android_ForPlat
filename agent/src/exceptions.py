class AgentError(Exception):
    """Root of all agent errors."""


class OperationNotAllowedError(AgentError):
    """The operation ID is not one of the allowlisted operations."""


class OperationNotMappedError(AgentError):
    """The operation ID is allowlisted but has no ADB command mapped yet."""


class AdbError(AgentError):
    """An ADB invocation failed."""
