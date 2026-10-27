"""Build safe, downloadable HTML reports from detached TestRunner result snapshots."""

from pathlib import Path
from uuid import UUID

from TestRunner.core.Base import StepStatus, TestStatus
from TestRunner.extensions.ReportGenerator import ReportGenerator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK_REPORT_DIR = PROJECT_ROOT / "reports" / "tasks"


def _as_status(enum_type, value, fallback):
    """Normalize enum members, Chinese labels, and public English status strings."""
    if isinstance(value, enum_type):
        return value

    raw_value = getattr(value, "value", value)
    if raw_value is None:
        return fallback

    text = str(raw_value).strip()
    normalized = text.casefold()
    aliases = {
        "passed": "pass",
        "success": "pass",
        "failed": "fail",
        "exception": "error",
        "异常": "error",
        "skipped": "skip",
    }
    normalized = aliases.get(normalized, normalized)

    for member in enum_type:
        if normalized in {
            str(member.name).casefold(),
            str(member.value).casefold(),
        }:
            return member
        member_aliases = {
            "pass": {"passed", "success"},
            "fail": {"failed"},
            "error": {"exception", "异常"},
            "skip": {"skipped"},
        }
        if normalized in member_aliases.get(member.name.casefold(), set()):
            return member
    return fallback


def build_report_results(details):
    """Adapt TestRunner's public result shape to ReportGenerator's contract."""
    if not isinstance(details, dict):
        details = {}

    results = []
    for case in details.get("test_cases") or []:
        if not isinstance(case, dict):
            continue

        steps = []
        for step in case.get("steps") or []:
            if not isinstance(step, dict):
                continue
            steps.append({
                "name": step.get("name") or "未命名步骤",
                "status": _as_status(
                    StepStatus,
                    step.get("status"),
                    StepStatus.ERROR,
                ),
                "error": step.get("error") or step.get("skip_reason"),
            })

        results.append({
            "name": (
                case.get("test_instance_name")
                or case.get("test_class_name")
                or "未命名用例"
            ),
            "status": _as_status(
                TestStatus,
                case.get("test_status"),
                TestStatus.ERROR,
            ),
            "duration": case.get("duration") or 0,
            "steps": steps,
            "error": case.get("error"),
        })
    return results


def build_report_stats(details, runner_stats=None):
    """Return integer summary values without requiring a live TestRunner object."""
    source = runner_stats if isinstance(runner_stats, dict) else None
    if source is not None:
        return {
            key: _safe_count(source.get(key, 0))
            for key in ("total", "passed", "failed", "error", "skipped")
        }

    if not isinstance(details, dict):
        details = {}
    cases = details.get("test_cases") or []
    case_stats = (details.get("progress") or {}).get("case_stats") or {}
    counts = {
        "total": case_stats.get("total_cases", len(cases)),
        "passed": case_stats.get("passed", 0),
        "failed": case_stats.get("failed", 0),
        "error": case_stats.get("error", 0),
        "skipped": case_stats.get("skipped", 0),
    }
    if not case_stats:
        counts = {
            "total": len(cases),
            "passed": 0,
            "failed": 0,
            "error": 0,
            "skipped": 0,
        }
        for case in cases:
            if not isinstance(case, dict):
                continue
            status = _as_status(TestStatus, case.get("test_status"), TestStatus.ERROR)
            if status == TestStatus.PASS:
                counts["passed"] += 1
            elif status == TestStatus.FAIL:
                counts["failed"] += 1
            elif status == TestStatus.SKIP:
                counts["skipped"] += 1
            elif status == TestStatus.ERROR:
                counts["error"] += 1
    return {key: _safe_count(value) for key, value in counts.items()}


def _safe_count(value):
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError, OverflowError):
        return 0


def generate_task_report(task_id, details, runner_stats=None, report_dir=None):
    """Generate a report beneath a controlled directory using a validated UUID filename."""
    try:
        safe_task_id = str(UUID(str(task_id)))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("无效的任务 ID") from exc

    target_dir = Path(report_dir).expanduser() if report_dir is not None else DEFAULT_TASK_REPORT_DIR
    target_dir = target_dir.resolve()
    target_path = target_dir / f"{safe_task_id}.html"

    report = ReportGenerator(
        results=build_report_results(details),
        stats=build_report_stats(details, runner_stats),
        report_path=str(target_path),
    )
    report.generate_report()
    if not target_path.is_file():
        raise OSError("HTML 报告未成功写入")
    return target_path
