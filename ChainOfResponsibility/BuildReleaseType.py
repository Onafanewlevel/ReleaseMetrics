import requests
import pandas as pd
from ChainOfResponsibility.BuildHandleBase import BuildHandler

class BuildReleaseTypeHandler(BuildHandler):
    """
    Handler for building the Release Type segment.

    This class extends the BuildHandler base class as part of a Chain of 
    Responsibility pattern. It processes the input table to construct a DataFrame 
    representing the 'Release Type' information from various projects. Each project's 
    'Release Type' data is extracted and used to build a DataFrame, whose index is mapped 
    using the provided project keys.

    The DataFrame is further enhanced by:
    - Adding a 'Total' row that sums the values across each column.
    - Adding a 'Total' column that sums the values across each row.
    - Transposing the DataFrame for a desired orientation.
    - Storing the final DataFrame in the confluence_content dictionary under the key 'Release Type'.

    If an HTTP-related error is encountered during processing using the requests module,
    the error is caught and an error message is printed.

    Args:
        project_keys (iterable): An iterable mapping of the project's keys to their names.
        table (dict): A dictionary in which each key-value pair contains data for a project.
                      Each value is expected to contain a 'Release Type' key.

    Returns:
        dict: The updated confluence_content dictionary containing the processed 
              'Release Type' DataFrame. If a successor exists in the chain, the handler
              will also delegate processing to the next handler.
    """

    def handle(self, project_keys, table):
        try:
            # Create DataFrame for Release Types
            release_types_data = {key: value['Release Type'] for key, value in table.items()}
            release_types_df = pd.DataFrame.from_dict(release_types_data, orient='index')
            release_types_df.index = release_types_df.index.map(project_keys)
            release_types_df.loc['Total'] = release_types_df.sum()
            release_types_df['Total'] = release_types_df.sum(axis=1)
            self.confluence_content['Release Type'] = release_types_df.transpose()
        except requests.exceptions.HTTPError as http_error:
            print(f"BuildReleaseTypeHandler error: {http_error}")
        return super().handle(project_keys, table)
