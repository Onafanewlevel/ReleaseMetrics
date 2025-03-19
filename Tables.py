from ChainOfResponsibility.BuildReleaseType import BuildReleaseTypeHandler
from ChainOfResponsibility.BuildPlannedUnplanned import BuildPlannedUnplannedHandler
from ChainOfResponsibility.BuildStoryBug import BuildStoryBugHandler

class Tables:
    """
    Build the release metrics table using the Chain of Responsibility pattern.

    The method initializes the handlers for different segments of the metrics and links them
    together. It then starts the processing chain, updating the provided table_data with
    computed counts.

    Args:
        table_data (dict): A dictionary representing the table structure where keys represent
                            different segments of the metrics and their associated counts.

    Returns:
        dict: The updated table_data with computed metrics.
    """
    def __init__(self, project_keys, tables):
        self.project_keys = project_keys
        self.tables = tables
        self.get_content = self.__build()

    def __build(self):
        build_releasetype_df = BuildReleaseTypeHandler()
        build_plannedunplanned_df = BuildPlannedUnplannedHandler()
        build_storybug_df = BuildStoryBugHandler()

        build_releasetype_df.set_successor(build_plannedunplanned_df)
        build_plannedunplanned_df.set_successor(build_storybug_df)

        final_table = build_releasetype_df.handle(self.project_keys, self.tables)

        return final_table
