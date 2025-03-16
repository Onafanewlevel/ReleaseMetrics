from ChainOfResponsibility.count_by_release_type import CountByReleaseTypeHandler
from ChainOfResponsibility.count_by_release_window import CountByReleaseWindowHandler
from ChainOfResponsibility.count_by_story_bug_type import CountByStoryBugTypeHandler
from AtlassianService.JQLQuery import JQLQuery
from AtlassianService.JiraIssues import JiraIssues

class ReleaseMetrics:
    def __init__(self, jira_client, project_key, issue_type, issue_fields, release_type=None, release_window=None):
        self.jira_client = jira_client
        self.project_key = project_key
        self.issue_type = issue_type
        self.issue_fields = issue_fields
        self.release_type = release_type
        self.release_window = release_window

    def _get_count_by_release_window(self):
        query = JQLQuery(
            self.project_key,
            self.issue_type,
            self.issue_fields,
            self.release_type,
            self.release_window
        ).get_jql_query()
        return JiraIssues(query, self.jira_client).get_jira_issues_count()

    def _get_count_by_issue_type(self):
        query = JQLQuery(
            self.project_key,
            self.issue_type,
            self.issue_fields,
            self.release_type,
            self.release_window
        ).get_jql_query()
        return JiraIssues(query, self.jira_client).get_jira_issues_count()

    def build_table(self, table_data):
        for key in table_data.keys():
            table_data[key] = 0
        print(table_data)

        # Build the chain. The order here defines the order in which each segment of the metrics is collected.
        release_type_handler = CountByReleaseTypeHandler()
        release_window_handler = CountByReleaseWindowHandler()
        story_bug_handler = CountByStoryBugTypeHandler()
        
        # Link the handlers
        release_type_handler.set_successor(release_window_handler)
        release_window_handler.set_successor(story_bug_handler)
        
        # Start the chain with an empty table list.
        final_table = release_type_handler.handle(self, table_data)
        return final_table