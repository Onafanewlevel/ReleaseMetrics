from ChainOfResponsibility.metrics_handler_base import MetricsHandler

class CountByReleaseWindowHandler(MetricsHandler):
    def handle(self, metrics, table):
        try:
            count_by_release_window = metrics._get_count_by_release_window()
            table[metrics.release_window] = count_by_release_window
        except Exception as e:
            raise Exception(f"CountByReleaseWindowHandler error: {str(e)}")
        return super().handle(metrics, table)