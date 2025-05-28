class BuildHandler:
    """
    Base class for the chain of responsibility used to build or process components
    in a sequence, delegating tasks along the chain.

    This handler follows the Chain of Responsibility design pattern. Each handler
    in the chain is responsible for a part of the overall process. It processes
    its own component of the work and, if necessary, delegates further tasks to
    the next handler in the chain using the '_successor' attribute.

    Attributes:
        _successor (BuildHandler, optional): The next handler in the chain that
            will take over if the current handler doesn't fully process the task.
        confluence_content (dict): A dictionary holding the processed components
            or other relevant content managed by the handler.

    Methods:
        set_successor(successor):
            Sets or updates the next handler in the chain.

        handle(project_keys, table):
            Processes the provided data related to project keys and a table.
            If the current handler cannot fully handle the data, the processing
            is delegated to the successor handler.
    """

    def __init__(self, successor=None):
        self._successor = successor
        self.confluence_content = {}

    def set_successor(self, successor):
        """
        Set or update the successor handler in the chain.

        Args:
            successor (BuildHandler): The next handler in the chain.
        """
        self._successor = successor

    def handle(self, project_keys, table):
        """
        Process the current component and delegate the remaining work if necessary.

        This method performs the processing related to the current handler's
        responsibility and, if there is a successor set, it forwards the process
        to the next handler.

        Args:
            project_keys (Any): The project keys that may be needed for processing.
            table (Any): The table data that is to be processed.

        Returns:
            dict: A dictionary containing the confluence content aggregated from
            the processing steps along the chain.
        """
        if self._successor:
            return self._successor.handle(project_keys, table)
        return self.confluence_content
