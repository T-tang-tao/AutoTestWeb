import unittest

from utils.task_state import (
    InvalidTaskTransition,
    TaskStatus,
    status_from_runner,
    validate_transition,
)


class TaskStateTests(unittest.TestCase):
    def test_pending_can_start(self):
        self.assertEqual(
            validate_transition(TaskStatus.PENDING, TaskStatus.RUNNING),
            TaskStatus.RUNNING,
        )

    def test_pending_can_fail_before_execution_starts(self):
        for terminal in (TaskStatus.ERROR, TaskStatus.CANCELLED):
            with self.subTest(terminal=terminal):
                self.assertEqual(
                    validate_transition(TaskStatus.PENDING, terminal),
                    terminal,
                )

    def test_running_can_finish_with_each_terminal_state(self):
        for terminal in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.ERROR,
            TaskStatus.CANCELLED,
        ):
            with self.subTest(terminal=terminal):
                self.assertEqual(
                    validate_transition(TaskStatus.RUNNING, terminal),
                    terminal,
                )

    def test_terminal_state_cannot_change(self):
        for current in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.ERROR,
            TaskStatus.CANCELLED,
        ):
            with self.subTest(current=current):
                with self.assertRaises(InvalidTaskTransition):
                    validate_transition(current, TaskStatus.RUNNING)

    def test_pending_cannot_complete_without_running(self):
        with self.assertRaises(InvalidTaskTransition):
            validate_transition(TaskStatus.PENDING, TaskStatus.COMPLETED)

    def test_runner_status_maps_to_task_status(self):
        self.assertEqual(status_from_runner("通过"), TaskStatus.COMPLETED)
        self.assertEqual(status_from_runner("失败"), TaskStatus.FAILED)
        self.assertEqual(status_from_runner("错误"), TaskStatus.ERROR)
        self.assertEqual(status_from_runner(None), TaskStatus.ERROR)


if __name__ == "__main__":
    unittest.main()
