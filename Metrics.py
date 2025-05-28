import os
import calendar
from datetime import datetime
import yaml
import requests
import pandas as pd
from atlassian import Jira, Confluence
import pytz

# Specify the Auckland time zone
time_zone = pytz.timezone('Pacific/Auckland')

# Get the current date
current_datetime = datetime.now(time_zone)
current_date = current_datetime.date()
current_month = current_date.month
current_year = current_date.year

print("current date: ", current_date)
print("current date & time: ", current_datetime)

#------------------------------------------
# Load config file and initialise config variables
#------------------------------------------

with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

project_keys = config['ProjectKeys']
issue_type = config['QueryFilters']['Issue_Type']
release_type = config['QueryFilters']['Release_Type']
release_window = config['QueryFilters']['Release_Window']
issue_fields = config['IssueFields']
confluence_report_page_id = config['AtlassianVariables']['Report_Page_Id']
confluence_report_space = config['AtlassianVariables']['Report_Space']

# Atlassian config variables
atlassian_url = config['AtlassianVariables']['Url']
atlassian_username = os.getenv(config['AtlassianVariables']['Username'])
atlassian_token = os.getenv(config['AtlassianVariables']['Password'])

#--------------------------------------
# Initialise Jira and Confluence client
#--------------------------------------

jira = Jira(
    url = atlassian_url,
    username = atlassian_username,
    password = atlassian_token
)

confluence = Confluence(
    url = atlassian_url,
    username = atlassian_username,
    password = atlassian_token
)

#--------------
# Functions
#--------------

def create_metric_tables():

    #-------------------------
    # Initialise the metrics table
    #-------------------------

    metric_table = {key: [] for key in project_keys}
    for key in metric_table:
        metric_table[key] = []

    for key in project_keys.keys():
        metric_table[key] = {
            'Release Type': {},
            'Release Window': {},
            'Issue Type': {},
        }

        for release in release_type:
            release_type_count = get_metric_count(key, 'Release', release, None)
            metric_table[key]['Release Type'][release] = release_type_count
        
        for window in release_window:
            planned_unlanned_count = get_metric_count(key, 'Release', None, window)
            metric_table[key]['Release Window'][window] = planned_unlanned_count

        for issue in issue_type:
            issue_type_count = get_metric_count(key, issue, None, None)
            metric_table[key]['Issue Type'][issue] = issue_type_count

    return metric_table

def get_metric_count(project_key, i_type, r_type, r_window):
    query = update_jql_query(project_key, i_type, r_type, r_window)
    issues = jira.jql(query, fields=['key'], limit=1)
    return issues['total']

def update_jql_query(project_key, i_type, r_type, r_window):
    i_type = 'Empty' if i_type == 'Other' else i_type
    base_query = (
    f'fixversion in releasedVersions("{project_key}") AND '
    f'issuetype in ({i_type}) AND '
    f'(resolved > startOfMonth() AND resolved < endOfMonth()) AND '
    f'fixversion != EMPTY')
    
    if r_type:
        base_query += f' AND "Release Type[Dropdown]" = {r_type}'
    if r_window:
        base_query += f' AND "Release Window[Dropdown]" = "{r_window}"'
    return base_query

def format_table_content(tables):
    # Initialise Farmatted Table Dictionary
    formatted_dict = {}
    print(f'Unformatted Table:\n f{tables}')

    # Create DataFrame for Release Types
    release_type_data = {key: value['Release Type'] for key, value in tables.items()}
    release_type_df = pd.DataFrame.from_dict(release_type_data, orient='index')
    release_type_df.index = release_type_df.index.map(project_keys)
    release_type_df.loc['Total'] = release_type_df.sum()
    release_type_df['Total'] = release_type_df.sum(axis=1)
    formatted_dict['Release Type'] = release_type_df.transpose()

    # Create DataFrame for Release Window
    release_window_data = {key: value['Release Window'] for key, value in tables.items()}
    release_window_df = pd.DataFrame.from_dict(release_window_data, orient='index')
    release_window_df.index = release_window_df.index.map(project_keys)
    release_window_df.loc['Total'] = release_window_df.sum()
    release_window_df['Total'] = release_window_df.sum(axis=1)
    formatted_dict['Planned/Unplanned'] = release_window_df.transpose()

    # Create DataFrame for Issue Types
    issue_types_data = {key: value['Issue Type'] for key, value in tables.items()}
    issue_types_df = pd.DataFrame.from_dict(issue_types_data, orient='index')
    issue_types_df.index = issue_types_df.index.map(project_keys)
    issue_types_df.loc['Total'] = issue_types_df.sum()
    issue_types_df['Total'] = issue_types_df.sum(axis=1)
    formatted_dict['Story/Bug'] = issue_types_df.transpose()

    print(f'Formatted Table:\n f{formatted_dict}')
    return formatted_dict

def post_to_confluence(tables):
    month_name = calendar.month_name[current_month]
    month_page_name = f"{current_year} - {month_name} Release Metrics"
    monthly_page_exists = confluence.page_exists(title=month_page_name, space=confluence_report_space)
    data_gathering_banner = '<ac:structured-macro ac:name="info" ac:schema-version="1" ac:macro-id="904c012c-b588-4a92-95ca-ce5da83125a8"><ac:rich-text-body><p>If you wanted to learn more about the data gathering process for each table, you could check this page <ac:link ac:card-appearance="inline"><ri:page ri:content-title="[EART] Release Metrics - Data Gathering Process" ri:version-at-save="38" /><ac:link-body>[EART] Release Metrics - Data Gathering Process</ac:link-body></ac:link>.</p></ac:rich-text-body></ac:structured-macro>'

    if monthly_page_exists:
        monthly_page = confluence.get_page_by_title(
            title=month_page_name,
            space=confluence_report_space)
        monthly_page_id = monthly_page['id']
        print(f"Monthly page already exists: {monthly_page_id}. Updating the data now...")

        try:
            # Create HTML for all tables with headers
            html = data_gathering_banner
            html += '<h2>Release Metrics</h2>'
            html += tables['Release Type'].to_html()

            html += '<h2>Planned/Unplanned Releases</h2>'
            html += tables['Planned/Unplanned'].to_html()

            html += '<h2>Story/Bug Breakdown</h2>'
            html += tables['Story/Bug'].to_html()

            # Update the Confluence page with the new content
            confluence.update_existing_page(
                page_id=monthly_page_id,
                title=month_page_name,
                body=html,
                representation='storage',
                full_width= True)
        except requests.exceptions.HTTPError as http_error:
            print(f'Error updating Confluence page: {http_error}')
    else:
        print(f"Monthly page does not exist: {month_page_name}. Creating a new page now...")

        try:
            # Create HTML for all tables with headers
            html = data_gathering_banner
            html += '<h2>Release Metrics</h2>'
            html += tables['Release Type'].to_html()

            html += '<h2>Planned/Unplanned Releases</h2>'
            html += tables['Planned/Unplanned'].to_html()

            html += '<h2>Story/Bug Breakdown</h2>'
            html += tables['Story/Bug'].to_html()

            # Create the new page
            confluence.create_page(
                space=confluence_report_space,
                title=month_page_name,
                body=html,
                representation="storage",
                full_width=True,
                parent_id=confluence_report_page_id,
                editor="v2")
            print(f"New page created: {month_page_name}")
        except requests.exceptions.HTTPError as http_error:
            print(f"Error creating new page: {http_error}")

#--------------------
# Main
#-------------------

if __name__ == '__main__':
    unformatted_table = create_metric_tables()
    formatted_tables = format_table_content(unformatted_table)
    post_to_confluence(formatted_tables)