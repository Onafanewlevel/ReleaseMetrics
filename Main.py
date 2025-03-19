import os
import yaml
import requests
from Tables import Tables
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
        self.final_table = {key: [] for key in self.project_keys}
        for key in self.final_table:
            self.final_table[key] = []

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
            raise
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error connecting to Jira client {conn_err}")
            raise
        except requests.exceptions.Timeout as time_err:
            print(f"Error: Connection timeout {time_err}")
            raise

        for key in self.project_keys.keys():
            self.final_table[key] = {
                'Release Type': {},
                'Release Window': {},
                'Issue Type': {}
            }

            # Get counts by release type (Major, Minor, Patch, Other)
            for release in self.release_type:
                release_type_count = ReleaseMetrics(jira_client, key, 'Release', self.issue_fields, release)
                self.final_table[key]['Release Type'][release] = release_type_count.jira_issues_count
            # Get planned vs unplanned counts for releases
            for window in self.release_window:
                planned_unplanned_count = ReleaseMetrics(jira_client, key, 'Release', self.issue_fields, None, window)
                self.final_table[key]['Release Window'][window] = planned_unplanned_count.jira_issues_count
            # Get story and bug counts
            for i_type in self.issue_type:
                issue_type_count = ReleaseMetrics(jira_client, key, i_type, self.issue_fields, None, None)
                i_type = 'Other' if i_type == 'Empty' else i_type
                self.final_table[key]['Issue Type'][i_type] = issue_type_count.jira_issues_count

        # --------------------
        # Build the tables using the Chain of Responsibility pattern
        # --------------------
        confluence_content = Tables(self.project_keys, self.final_table).get_content()

        return confluence_content

    def post_to_confluence(self, confluence_content):
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
        confluence.post_confluence_page(self.confluence_report_page_id, self.confluence_report_space, confluence_content)

if __name__ == "__main__":
    main = Main()
    content = main.generate_tables()
    main.post_to_confluence(content)
