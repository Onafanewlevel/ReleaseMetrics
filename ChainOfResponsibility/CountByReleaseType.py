import requests
from ChainOfResponsibility.MetricsHandlerBase import MetricsHandler

class CountByReleaseTypeHandler(MetricsHandler):
    def handle(self, metrics, table):
        try:
            issues_count = metrics.get_count_by_issue_type()
            issue_type = "Other" if metrics.issue_type == "Empty" else metrics.issue_type
            table[issue_type] = issues_count
        except requests.exceptions.HTTPError as http_error:
            print(f"CountByIssueTypeHandler error: {http_error}")
        return super().handle(metrics, table)