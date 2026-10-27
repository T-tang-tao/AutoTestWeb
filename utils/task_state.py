"""Task status definitions and transition rules for background test runs."""

from enum import Enum


class TaskStatus(str, Enum):
    """Public lifecycle states for a submitted test task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"


TERMINAL_TASK_STATUSES = frozenset(
    {
        TaskStatus.COMPLETED,
        TaskStatus.FAILED,
        TaskStatus.ERROR,
        TaskStatus.CANCELLED,
    }
)

_ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: frozenset(
        {TaskStatus.RUNNING, TaskStatus.ERROR, TaskStatus.CANCELLED}
    ),
    TaskStatus.RUNNING: TERMINAL_TASK_STATUSES,
    TaskStatus.COMPLETED: frozenset(),
    TaskStatus.FAILED: frozenset(),
    TaskStatus.ERROR: frozenset(),
    TaskStatus.CANCELLED: frozenset(),
}


class InvalidTaskTransition(ValueError):
    """Raised when a task attempts an unsupported state transition."""


def validate_transition(current, target):
    """Return the target state or raise when the transition is not allowed."""
    current_status = TaskStatus(current)
    target_status = TaskStatus(target)

    if target_status not in _ALLOWED_TRANSITIONS[current_status]:
        raise InvalidTaskTransition(
            "Invalid task status transition: "
            f"{current_status.value} -> {target_status.value}"
        )

    return target_status


def status_from_runner(runner_status):
    """Map the TestRunner suite result to the task lifecycle's terminal state."""
    normalized = str(runner_status or "").strip().lower()

    if normalized in {"通过", "pass", "passed", "success", "completed"}:
        return TaskStatus.COMPLETED
    if normalized in {"失败", "fail", "failed"}:
        return TaskStatus.FAILED
    return TaskStatus.ERROR
