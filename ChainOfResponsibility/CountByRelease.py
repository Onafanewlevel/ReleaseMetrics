import requests
from ChainOfResponsibility.MetricsHandlerBase import MetricsHandler

class CountByReleaseWindowHandler(MetricsHandler):
    def handle(self, metrics, table):
        try:
            count_by_release_window = metrics.get_count_by_release_window()
            table[metrics.release_window] = count_by_release_window
        except requests.exceptions.HTTPError as http_error:
            print(f"CountByReleaseWindowHandler error: {http_error}")
        return super().handle(metrics, table)
