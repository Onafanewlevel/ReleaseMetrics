from AtlassianService.JiraService import JiraClient

class JiraIssues:
    def __init__(self, jql_query, jira_client):
        self.jql_query = jql_query
        self.jira_client = jira_client

    def get_jira_issues_count(self):
        try:
            issues = self.jira_client.jql(self.jql_query, fields=['key'], limit=1)
            return issues['total']
        except Exception as e:
            raise Exception(f"Failed to get Jira issues: {str(e)}")