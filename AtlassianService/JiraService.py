from atlassian import Jira

class JiraClient:
    def __init__(self, url, username, password):
        self._url = url
        self._username = username 
        self._password = password
    
    def authenticate(self):
        try:
            self.jira = Jira(
                url=self._url,
                username=self._username,
                password=self._password
            )
            return self.jira
        except Exception as e:
            raise Exception(f"Failed to authenticate Jira client: {str(e)}")