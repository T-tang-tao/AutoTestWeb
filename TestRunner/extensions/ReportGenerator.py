import os
from html import escape
from pathlib import Path


STATUS_ALIASES = {
    "pass": "pass",
    "passed": "pass",
    "success": "pass",
    "通过": "pass",
    "fail": "fail",
    "failed": "fail",
    "失败": "fail",
    "error": "error",
    "错误": "error",
    "异常": "error",
    "skip": "skip",
    "skipped": "skip",
    "跳过": "skip",
    "pending": "pending",
    "待执行": "pending",
    "running": "running",
    "进行中": "running",
}
STATUS_LABELS = {
    "pass": "通过",
    "fail": "失败",
    "error": "错误",
    "skip": "跳过",
    "pending": "待执行",
    "running": "进行中",
    "unknown": "未知",
}


class ReportGenerator:
    """Generate a small static HTML report from TestRunner results."""

    def __init__(self, results, stats, report_path="reports/test_report.html"):
        self.results = results
        self.stats = stats
        self.report_path = report_path
        self.template = self._load_template()

    def _load_template(self):
        template_path = Path(__file__).parent / "templates" / "report_template.html"
        with open(template_path, "r", encoding="utf-8") as file:
            return file.read()

    def generate_report(self):
        """Render a report, escape all dynamic text and return the generated path."""
        filled_template = self.template.format(
            total=escape(str(self.stats.get("total", 0))),
            passed=escape(str(self.stats.get("passed", 0))),
            failed=escape(str(self.stats.get("failed", 0))),
            error=escape(str(self.stats.get("error", 0))),
            skipped=escape(str(self.stats.get("skipped", 0))),
            results="".join(self._format_result(result) for result in self.results),
        )

        report_path = Path(self.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(filled_template, encoding="utf-8")
        print(f"HTML测试报告已生成：{os.path.abspath(report_path)}")
        return report_path.resolve()

    @staticmethod
    def _status_info(status):
        """Convert enum values and Chinese/English strings to safe CSS keys and labels."""
        raw_value = getattr(status, "value", status)
        raw_name = getattr(status, "name", None)
        candidates = [raw_name, raw_value]

        for candidate in candidates:
            if candidate is None:
                continue
            normalized = str(candidate).strip().casefold()
            status_key = STATUS_ALIASES.get(normalized)
            if status_key:
                return status_key, STATUS_LABELS[status_key]

        label = str(raw_value if raw_value is not None else "")
        return "unknown", label or STATUS_LABELS["unknown"]

    def _format_result(self, result):
        steps_html = []
        for step in result.get("steps", []):
            step_status_key, step_status_label = self._status_info(step.get("status", "error"))
            step_name = escape(str(step.get("name", "")))
            step_error = step.get("error") or step.get("skip_reason")
            error_html = (
                f'<small class="step-error-detail">{escape(str(step_error))}</small>'
                if step_error
                else ""
            )
            steps_html.append(
                f'<li class="step-{step_status_key}">'
                f'<span class="step-indicator"></span>'
                f"{step_name} <span class=\"step-status-label\">"
                f"({escape(step_status_label)})</span>{error_html}</li>"
            )

        case_status_key, case_status_label = self._status_info(result.get("status", "error"))
        case_name = escape(str(result.get("name", "")))
        duration = escape(str(result.get("duration", 0)))
        case_error = result.get("error")
        case_error_html = (
            f'<div class="case-error">{escape(str(case_error))}</div>'
            if case_error
            else ""
        )

        return (
            "<tr>"
            f"<td>{case_name}{case_error_html}</td>"
            f'<td><span class="status-{case_status_key}">'
            f"{escape(case_status_label)}</span></td>"
            f"<td>{duration}s</td>"
            f'<td><ul class="steps">{"".join(steps_html)}</ul></td>'
            "</tr>"
        )
