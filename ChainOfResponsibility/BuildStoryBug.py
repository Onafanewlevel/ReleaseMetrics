"""
A handler for counting issues by story/bug type.

Attributes:
    MetricsHandler (class): The base class for all metrics handlers.
"""
import requests
import pandas as pd
from ChainOfResponsibility.BuildHandleBase import BuildHandler

class BuildStoryBugHandler(BuildHandler):
    """
    A handler for counting issues by story/bug type.
    """
    def handle(self, project_keys, table):
        try:
            # Create DataFrame for Issue Types
            issue_types_data = {key: value['Issue Type'] for key, value in table.items()}
            issue_types_df = pd.DataFrame.from_dict(issue_types_data, orient='index')
            issue_types_df.index = issue_types_df.index.map(project_keys)
            issue_types_df.loc['Total'] = issue_types_df.sum()
            issue_types_df['Total'] = issue_types_df.sum(axis=1)
            self.confluence_content['Story/Bug'] = issue_types_df.transpose()
        except requests.exceptions.HTTPError as http_error:
            print(f"BuildStoryBugHandler error: {http_error}")
        return super().handle(project_keys, table)
