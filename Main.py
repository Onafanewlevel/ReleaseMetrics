import yaml
from AtlassianService.JiraService import JiraClient
from AtlassianService.ConfluenceService import ConfluenceClient
from ReleaseMetrics import ReleaseMetrics
import pandas as pd
import os

class Main:
    def __init__(self):
        # --------------------
        # Load the config file
        # --------------------
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # --------------------
        # Initialise the table
        # --------------------
        self.table = {}

        # --------------------
        # Initialise the config variables
        # --------------------
        self.project_keys = config['ProjectKeys']
        self.issue_type = config['QueryFilters']['Issue_Type']
        self.release_type = config['QueryFilters']['Release_Type']
        self.release_window = config['QueryFilters']['Release_Window']
        self.issue_fields = config['IssueFields']
        self.table_data = config['TableData']

        # --------------------
        # Initialise the Confluence client and variables
        # --------------------
        self.confluence_report_page_id = config['Confluence']['Report_Page_Id']
        self.confluence_report_space = config['Confluence']['Report_Space']
        self.atlassian_url = config['Confluence']['Url']
        self.atlassian_username = os.getenv(config['Confluence']['Username'])
        self.atlassian_token = os.getenv(config['Confluence']['Password'])

    def generate_tables(self):
        # --------------------
        # Authenticate the Jira client
        # --------------------
        try:
            jira_client = JiraClient(self.atlassian_url, self.atlassian_username, self.atlassian_token).authenticate()
        except Exception as e:
            print(f"Error authenticating the Jira client: {e}")
            return
            

        # --------------------
        # Initialise the tables
        # --------------------
        # Initialize release type table.
        release_type_table = self.table_data['ReleaseType']
        # Initialize the release window table.
        release_window_table = self.table_data['ReleaseWindow']
        # Initialize the issue type table.
        issue_type_table = self.table_data['IssueType']
    
        # Loop through each project key and accumulate metrics from different queries.
        for key in self.project_keys.keys():
            release_type_metrics = []
            release_window_metrics = []
            issue_type_metrics = []
            
            # Get counts by release type (Major, Minor, Patch, Other)
            for release in self.release_type:
                metrics = ReleaseMetrics(jira_client, key, 'Release', self.issue_fields, release)
                release_counts = metrics.build_table(release_type_table)
                release_type_metrics.extend(release_counts)
                
            # Get planned vs unplanned counts for releases
            for window in self.release_window:
                metrics = ReleaseMetrics(jira_client, key, 'Release', self.issue_fields, None, window)
                planned_counts = metrics.build_table(release_window_table)
                release_window_metrics.extend(planned_counts)
                
            # Get story and bug counts
            for type in self.issue_type:
                metrics = ReleaseMetrics(jira_client, key, type, self.issue_fields, None, None)
                story_counts = metrics.build_table(issue_type_table)
                issue_type_metrics.extend(story_counts)
        
            # Add project name and its metrics to the final table.
            release_type_table.append(release_type_metrics)
            release_window_table.append(release_window_metrics)
            issue_type_table.append(issue_type_metrics)

        rt_table_df = pd.DataFrame(release_type_table, index=self.project_keys.values()).transpose()
        rw_table_df = pd.DataFrame(release_window_table, index=self.project_keys.values()).transpose()
        it_table_df = pd.DataFrame(issue_type_table, index=self.project_keys.values()).transpose()

        self.table['ReleaseType'] = rt_table_df
        self.table['ReleaseWindow'] = rw_table_df
        self.table['IssueType'] = it_table_df

    def post_to_confluence(self):
        # --------------------
        # Authenticate the Confluence client
        # --------------------
        try:
            confluence = ConfluenceClient(self.atlassian_url, self.atlassian_username, self.atlassian_token).authenticate()
        except Exception as e:
            print(f"Error authenticating the Confluence client: {e}")
            return

        # --------------------
        # Post the tables to Confluence
        # --------------------
        confluence.post_confluence_page(self.confluence_report_page_id, self.confluence_report_space, self.table)

if __name__ == "__main__":
    main = Main()
    main.generate_tables()
    main.post_to_confluence()
        