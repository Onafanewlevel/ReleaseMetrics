class JQLQuery:
    def __init__(self, project_key, issue_type, issue_fields, release_type=None, release_window=None):
        self.project_key = project_key
        self.issue_type = issue_type
        self.issue_fields = issue_fields
        self.release_type = release_type
        self.release_window = release_window
        self.jql_query = self.__build_query()

    def __build_query(self):
        base_query = f'fixversion in releasedVersions("{self.project_key}") AND issuetype in ({self.issue_type}) AND (resolved > startOfMonth() AND resolved < endOfMonth())'
        if self.release_type:
            return f'{base_query} AND "Release Type[Dropdown]" = "{self.release_type}"'
        if self.release_window:
            return f'{base_query} AND "Release Window[Dropdown]" = "{self.release_window}"'
        return base_query

    def get_jql_query(self):
        return self.jql_query