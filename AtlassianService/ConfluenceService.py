"""

Raises:
    Exception: _description_

Returns:
    _type_: _description_
"""
from datetime import datetime
import calendar
from atlassian import Confluence
import requests


class ConfluenceClient:
    def __init__(self, url, username, password):
        self._url = url
        self._username = username
        self._password = password
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        self.confluence = self.__authenticate()

    def __authenticate(self):
        try:
            self.confluence = Confluence(
                url=self._url,
                username=self._username,
                password=self._password
            )
            return self.confluence
        except requests.exceptions.HTTPError as e:
            print(f"Failed to authenticate Jira client: {str(e)}")
            return None

    def post_confluence_page(self, page_id, page_space, tables):
        """
        Update the Confluence page with the tables.
        """
        # confluence variables for the target page
        report_page_id = page_id
        report_space = page_space

        month_name = calendar.month_name[self.current_month]
        current_year = self.current_year

        month_page_name = f"{current_year} - {month_name} Release Metrics"

        monthly_page_exists = self.confluence.page_exists(title=month_page_name, space=report_space)

        if monthly_page_exists:
            monthly_page = self.confluence.get_page_by_title(
                title=month_page_name,
                space=report_space)
            monthly_page_id = monthly_page['id']
            print(f"Monthly page already exists: {monthly_page_id}. Updating the data now...")

            try:
                # Create HTML for all tables with headers
                html = '<h2>Release Metrics</h2>'
                html += tables['Release Type'].to_html()

                html += '<h2>Planned/Unplanned Releases</h2>'
                html += tables['Planned/Unplanned'].to_html()

                html += '<h2>Story/Bug Breakdown</h2>'
                html += tables['Story/Bug'].to_html()

                # Update the Confluence page with the new content
                self.confluence.update_existing_page(
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
                html = '<h2>Release Metrics</h2>'
                html += tables['Release Type'].to_html()

                html += '<h2>Planned/Unplanned Releases</h2>'
                html += tables['Planned/Unplanned'].to_html()

                html += '<h2>Story/Bug Breakdown</h2>'
                html += tables['Story/Bug'].to_html()

                # Create the new page
                self.confluence.create_page(
                    space=report_space,
                    title=month_page_name,
                    body=html,
                    representation="storage",
                    full_width=True,
                    parent_id=report_page_id,
                    editor="v2")
                print(f"New page created: {month_page_name}")
            except requests.exceptions.HTTPError as http_error:
                print(f"Error creating new page: {http_error}")
