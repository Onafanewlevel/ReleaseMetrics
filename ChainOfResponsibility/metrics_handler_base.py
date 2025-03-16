# Handlers base class for the chain of responsibility
class MetricsHandler:
    def __init__(self, successor=None):
        self._successor = successor

    def set_successor(self, successor):
        self._successor = successor

    def handle(self, metrics, table):
        # Process the current component and delegate remaining work if needed.
        if self._successor:
            return self._successor.handle(metrics, table)
        return table