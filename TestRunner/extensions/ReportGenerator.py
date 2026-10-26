import os
from pathlib import Path


class ReportGenerator:
    def __init__(self, results, stats, report_path='reports/test_report.html'):
        self.results = results  # 测试用例结果列表
        self.stats = stats      # 测试统计信息
        self.report_path = report_path  # 报告输出路径
        self.template = self._load_template()  # 加载HTML模板

    def _load_template(self):
        # 模板文件位于extensions/templates目录下
        template_path = Path(__file__).parent / 'templates' / 'report_template.html'
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_report(self):
        # 填充模板数据
        filled_template = self.template.format(
            total=self.stats['total'],
            passed=self.stats['passed'],
            failed=self.stats['failed'],
            error=self.stats['error'],
            skipped=self.stats['skipped'],
            results=''.join([self._format_result(result) for result in self.results])
        )

        # 创建报告目录（如果不存在）
        report_dir = Path(self.report_path).parent
        report_dir.mkdir(parents=True, exist_ok=True)

        # 写入报告文件
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(filled_template)
        print(f'HTML测试报告已生成：{os.path.abspath(self.report_path)}')

    def _format_result(self, result):
        # 格式化单个测试用例的HTML展示
        steps_html = ''.join([
            f'<li class="step-{step["status"].name.lower()}">'
            f'<span class="step-indicator"></span>'
            f'{step["name"]}</li>'
        for step in result["steps"]])

        return (
            f'<tr>'
            f'<td>{result["name"]}</td>'
            f'<td><span class="status-{result["status"].name.lower()}">{str(result["status"])}</span></td>'
            f'<td>{result["duration"]}s</td>'
            f'<td><ul class="steps">{steps_html}</ul></td>'
            '</tr>'
        )
