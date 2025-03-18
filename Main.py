import os
import pandas as pd
import yaml
import requests
from collections import defaultdict
from AtlassianService.JiraService import JiraClient
from AtlassianService.ConfluenceService import ConfluenceClient
from ReleaseMetrics import ReleaseMetrics

class Main:
    """
    This class is the main class for the project.
    It initialises the config, table, and confluence client.
    It also generates the tables and posts them to confluence.
    It also contains the main method that is used to run the program.
    """
    def __init__(self):
        # --------------------
        # Load the config file
        # --------------------
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
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
        # Initialise the table
        # --------------------
        final_table = {key: [] for key in self.project_keys}
        for key in final_table:
            final_table[key] = []

        # --------------------
        # Initialise the Confluence client and variables
        # --------------------
        self.confluence_report_page_id = config['Confluence']['Report_Page_Id']
        self.confluence_report_space = config['Confluence']['Report_Space']
        self.atlassian_url = config['Confluence']['Url']
        self.atlassian_username = os.getenv(config['Confluence']['Username'])
        self.atlassian_token = os.getenv(config['Confluence']['Password'])

    def generate_tables(self):
        """
        #---------------------
        # Authenticate the Jira Client
        #---------------------
        """

        try:
            jira_client = JiraClient(
                self.atlassian_url,
                self.atlassian_username,
                self.atlassian_token)
        except requests.exceptions.HTTPError as http_err:
            print(f"Error authenticating the Jira client: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error connecting to Jira client {conn_err}")
        except requests.exceptions.Timeout as time_err:
            print(f"Error: Connection timeout {time_err}")
            return

        # --------------------
        # Initialise the tables
        # --------------------
        # # Initialize release type table.
        # release_type_table = self.table_data['ReleaseType']
        # print(release_type_table)
        # # Initialize the release window table.
        # release_window_table = self.table_data['ReleaseWindow']
        # print(release_window_table)
        # # Initialize the issue type table.
        # issue_type_table = self.table_data['IssueType']
        # print(issue_type_table)
        # Loop through each project key and accumulate metrics from different queries.
        for key in self.project_keys.keys():
            # Get counts by release type (Major, Minor, Patch, Other)
            for release in self.release_type:
                metrics = ReleaseMetrics(jira_client, key, 'Release', self.issue_fields, release)
                release_counts = metrics.build_table(self.table_data)
                self.final_table[key][release] = release_counts
            # Get planned vs unplanned counts for releases
            for window in self.release_window:
                metrics = ReleaseMetrics(jira_client, key, 'Release', self.issue_fields, None, window)
                planned_counts = metrics.build_table(self.table_data)
                self.final_table[key][window] = planned_counts
            # Get story and bug counts
            for i_type in self.issue_type:
                metrics = ReleaseMetrics(jira_client, key, i_type, self.issue_fields, None, None)
                story_counts = metrics.build_table(self.table_data)
                self.final_table[key][i_type] = story_counts

            # Add project name and its metrics to the final table.
            

        rt_table_df = pd.DataFrame(release_type_table, index=self.project_keys.values()).transpose()
        rw_table_df = pd.DataFrame(release_window_table, index=self.project_keys.values()).transpose()
        it_table_df = pd.DataFrame(issue_type_table, index=self.project_keys.values()).transpose()

        self.table['ReleaseType'] = rt_table_df
        self.table['ReleaseWindow'] = rw_table_df
        self.table['IssueType'] = it_table_df

    def post_to_confluence(self):
        """
        This method posts to confluecne
        """
        # --------------------
        # Authenticate the Confluence client
        # --------------------
        try:
            confluence = ConfluenceClient(
                self.atlassian_url,
                self.atlassian_username,
                self.atlassian_token)

        except requests.exceptions.HTTPError as http_err:
            print(f"Error authenticating the Confluence client: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error connecting to Confluence client {conn_err}")
        except requests.exceptions.Timeout as time_err:
            print(f"Error: Connection timeout {time_err}")

        # --------------------
        # Post the tables to Confluence
        # --------------------
        confluence.post_confluence_page(self.confluence_report_page_id, self.confluence_report_space, self.table)

if __name__ == "__main__":
    main = Main()
    main.generate_tables()
    main.post_to_confluence()
