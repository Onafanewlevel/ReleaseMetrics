"""
release_metrics

Returns:
    _type_: _description_
"""
from collections import defaultdict
from ChainOfResponsibility.CountByReleaseType import CountByReleaseTypeHandler
from ChainOfResponsibility.CountByRelease import CountByReleaseWindowHandler
from AtlassianService.JQLQuery import JQLQuery

class ReleaseMetrics:
    """
    A class for collecting and building release metrics from Jira issues.

    This class leverages the Chain of Responsibility pattern to aggregate and process
    metrics related to Jira issues based on configured parameters like project key, issue type,
    and optional filters such as release type and release window.

    Attributes:
        jira_client (object): Instance to interact with Jira.
        project_key (str): The key of the Jira project.
        issue_type (str): The type of Jira issues to be queried.
        issue_fields (list or dict): Fields to include in the Jira query.
        release_type (optional): Filter for the specific release type.
        release_window (optional): Filter for a specific release window.
    """

    def __init__(self,
                jira_client,
                project_key,
                issue_type,
                issue_fields,
                release_type=None,
                release_window=None):
        """
        Initialize ReleaseMetrics with Jira client and filter parameters.

        Args:
            jira_client (object): Instance to interact with Jira.
            project_key (str): The key of the Jira project.
            issue_type (str): The type of Jira issues to be queried.
            issue_fields (list or dict): Fields to include in the Jira query.
            release_type (optional): Optional filter for the specific release type.
            release_window (optional): Optional filter for the release window.
        """
        self.jira_client = jira_client
        self.project_key = project_key
        self.issue_type = issue_type
        self.issue_fields = issue_fields
        self.release_type = release_type
        self.release_window = release_window
        self.jira_issues_count = self.__get_jira_issues_count()

    def __get_jira_issues_count(self):
        """
        Retrieve the count of Jira issues filtered by the release window.

        This method constructs a JQL query using the provided parameters and returns the count
        of Jira issues that match the criteria based on the release window.

        Returns:
            int: The count of Jira issues filtered by release window.
        """
        query = JQLQuery(
            self.project_key,
            self.issue_type,
            self.issue_fields,
            self.release_type,
            self.release_window
        ).get_jql_query()
        return self.jira_client.get_jira_issues_count(query)

    def build_table(self, table_data):
        """
        Build the release metrics table using the Chain of Responsibility pattern.

        The method initializes the handlers for different segments of the metrics and links them
        together. It then starts the processing chain, updating the provided table_data with
        computed counts.

        Args:
            table_data (dict): A dictionary representing the table structure where keys represent
                               different segments of the metrics and their associated counts.

        Returns:
            dict: The updated table_data with computed metrics.
        """
        # Initialize the table data with default values.
        table_data = defaultdict(int)

        # ------------------------
        # Build the chain.
        # The order here defines the order in which each segment of the metrics is collected.
        # ------------------------
        release_type_handler = CountByReleaseTypeHandler()
        release_window_handler = CountByReleaseWindowHandler()
        story_bug_handler = CountByReleaseTypeHandler()
        # Link the handlers
        release_type_handler.set_successor(release_window_handler)
        release_window_handler.set_successor(story_bug_handler)
        # Start the chain with an empty table list.
        final_table = release_type_handler.handle(self, table_data)
        return final_table
