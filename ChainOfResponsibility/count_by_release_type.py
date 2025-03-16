from ChainOfResponsibility.metrics_handler_base import MetricsHandler

class CountByReleaseTypeHandler(MetricsHandler):
    def handle(self, metrics, table):
        try:
            issues_count = metrics._get_count_by_issue_type()
            issue_type = "Other" if metrics.issue_type == "Empty" else metrics.issue_type
            table[issue_type] = issues_count
        except Exception as e:
            raise Exception(f"CountByIssueTypeHandler error: {str(e)}")
        return super().handle(metrics, table)