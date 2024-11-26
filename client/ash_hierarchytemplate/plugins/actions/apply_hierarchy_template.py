import ayon_api
from ayon_core.pipeline import LauncherAction


class ApplyHierarchyTemplate(LauncherAction):
    """Open AYON browser page to the current context."""

    name = "apply_hierarchy_template"
    label = "Apply Hierarchy Template"
    icon = "gears"
    order = 999

    def is_compatible(self, selection):
        self.log.info(f"selection: {selection}")
        folder_path = selection.get_folder_path()
        if folder_path == "/":
            return True
        return False

    def process(self, selection, **kwargs):
        ayon_api.dispatch_event(
            topic="apply_hierarchy_template",
            sender=self,
            project_name=selection["project_name"],
            username=selection["username"],
        )
        # open events page with filter?
