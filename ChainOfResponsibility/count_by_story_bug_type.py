from ChainOfResponsibility.metrics_handler_base import MetricsHandler

class CountByStoryBugTypeHandler(MetricsHandler):
    def handle(self, metrics, table):
        try:
            story_bug_count = metrics._get_story_bug_count()
            table[metrics.issue_type] = story_bug_count
        except Exception as e:
            raise Exception(f"CountByStoryBugTypeHandler error: {str(e)}")
        return super().handle(metrics, table)