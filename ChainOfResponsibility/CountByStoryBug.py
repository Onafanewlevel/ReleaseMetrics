"""
A handler for counting issues by story/bug type.

Attributes:
    MetricsHandler (class): The base class for all metrics handlers.
"""
import requests
from ChainOfResponsibility.MetricsHandlerBase import MetricsHandler

class CountByStoryBugTypeHandler(MetricsHandler):
    """
    A handler for counting issues by story/bug type.
    """
    def handle(self, metrics, table):
        try:
            story_bug_count = metrics.get_count_by_issue_type()
            table[metrics.issue_type] = story_bug_count
        except requests.exceptions.HTTPError as http_error:
            print(f"CountByStoryBugTypeHandler error: {http_error}")
        return super().handle(metrics, table)
