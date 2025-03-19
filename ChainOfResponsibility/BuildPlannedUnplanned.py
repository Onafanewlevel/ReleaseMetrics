import requests
import pandas as pd
from ChainOfResponsibility.BuildHandleBase import BuildHandler

class BuildPlannedUnplannedHandler(BuildHandler):
    """
    Handler for building the Planned/Unplanned release window segment.

    This class extends the BuildHandler base class as part of a Chain of 
    Responsibility. It processes the input table to construct a DataFrame 
    that represents the 'Release Window' information from various projects,
    identified by the given project keys. The DataFrame is manipulated to 
    include a 'Total' row and column which aggregates the data, and the 
    resulting table is stored in the confluence_content dictionary under the 
    key 'Planned/Unplanned'.

    The processing includes:
    - Extracting 'Release Window' data for each project from the table.
    - Creating a pandas DataFrame from the extracted dictionary.
    - Mapping the DataFrame's index using the provided project keys.
    - Summing rows and columns to create a total summary.
    - Storing the transposed DataFrame in confluence_content for later use.

    If an HTTP-related error from the requests module occurs during processing,
    it is caught and an error message is printed.

    Args:
        project_keys (iterable): An iterable mapping of the project's keys to their names.
        table (dict): A dictionary where each key-value pair contains data for the project.
                      Each value is expected to contain a 'Release Window' key.

    Returns:
        dict: The confluence_content updated with the 'Planned/Unplanned' key containing
              the processed DataFrame. If a successor exists in the chain, the processing
              is delegated to the next handler.
    """

    def handle(self, project_keys, table):
        try:
            # Create DataFrame for Release Window
            release_window_data = {key: value['Release Window'] for key, value in table.items()}
            release_window_df = pd.DataFrame.from_dict(release_window_data, orient='index')
            release_window_df.index = release_window_df.index.map(project_keys)
            release_window_df.loc['Total'] = release_window_df.sum()
            release_window_df['Total'] = release_window_df.sum(axis=1)
            self.confluence_content['Planned/Unplanned'] = release_window_df.transpose()
        except requests.exceptions.HTTPError as http_error:
            print(f"BuildPlannedUnplannedHandler error: {http_error}")
        return super().handle(project_keys, table)
