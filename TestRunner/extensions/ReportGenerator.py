import os
from html import escape
from pathlib import Path


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
        """Render the report with escaped case/step labels and summary values."""
        filled_template = self.template.format(
            total=self.stats["total"],
            passed=self.stats["passed"],
            failed=self.stats["failed"],
            error=self.stats["error"],
            skipped=self.stats["skipped"],
            results="".join(self._format_result(result) for result in self.results),
        )

        report_path = Path(self.report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(filled_template, encoding="utf-8")
        print("HTML测试报告已生成：%s", os.path.abspath(report_path))

    def _format_result(self, result):
        steps_html = []
        for step in result.get("steps", []):
            step_status = step["status"]
            status_name = str(getattr(step_status, "name", step_status)).lower()
            step_name = escape(str(step.get("name", "")))
            steps_html.append(
                f'<li class="step-{status_name}">'
                f'<span class="step-indicator"></span>{step_name}</li>'
            )

        case_status = result["status"]
        status_name = str(getattr(case_status, "name", case_status)).lower()
        status_label = escape(str(getattr(case_status, "value", case_status)))
        case_name = escape(str(result.get("name", "")))
        duration = escape(str(result.get("duration", 0)))

        return (
            "<tr>"
            f"<td>{case_name}</td>"
            f'<td><span class="status-{status_name}">{status_label}</span></td>'
            f"<td>{duration}s</td>"
            f'<td><ul class="steps">{"".join(steps_html)}</ul></td>'
            "</tr>"
        )
