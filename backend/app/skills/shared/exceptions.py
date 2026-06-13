"""Shared exceptions used by skill modules."""


class SkillError(Exception):
    """Base exception for skill registry errors."""


class InvalidSignalError(SkillError):
    """Raised when a generated signal is invalid."""


class ExecutionError(SkillError):
    """Raised when an execution payload cannot be built."""
