from atlassian import Jira
import requests

class JiraClient:
    """
    A client for connecting to a Jira server using provided credentials.

    This class encapsulates the authentication process with a Jira server.
    After instantiation, it automatically authenticates with the server.

    Args:
        url (str): The URL of the Jira server.
        username (str): The username for Jira authentication.
        password (str): The password for Jira authentication.

    Attributes:
        _url (str): The URL of the Jira server.
        _username (str): The Jira username.
        _password (str): The Jira password.
        jira (Jira): The authenticated Jira client instance.
    """

    def __init__(self, url, username, password):
        self._url = url
        self._username = username
        self._password = password
        self.jira = self.__authenticate()

    def __authenticate(self):
        try:
            self.jira = Jira(
                url=self._url,
                username=self._username,
                password=self._password
            )
            return self.jira
        except requests.exceptions.HTTPError as e:
            print(f"Failed to authenticate Jira client: {str(e)}")
            return None

    def get_jira_issues_count(self, jql_query):
        """
        Retrieve the count of Jira issues based on the provided JQL query.

        Args:
            jql_query (str): The JQL query to retrieve issues from Jira.

        Returns:
            int: The count of Jira issues that match the JQL query.
        """
        try:
            issues = self.jira.jql(jql_query, fields=['key'], limit=1)
            return issues['total']
        except requests.exceptions.HTTPError as http_error:
            print(f"Failed to get Jira issues: {http_error}")
            return None
