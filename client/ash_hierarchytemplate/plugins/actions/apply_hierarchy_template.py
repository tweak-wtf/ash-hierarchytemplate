import ayon_api
from ayon_core.pipeline import LauncherAction


class ApplyHierarchyTemplate(LauncherAction):
    """Open AYON browser page to the current context."""
    name = "apply_hierarchy_template"
    label = "Apply Hierarchy Template"
    icon = "gears"
    order = 999

    # TODO: add filter where this is accessible from

    def process(self, selection, **kwargs):
      ayon_api.dispatch_event(
         topic="apply_hierarchy_template",
         sender=self,
         project_name=selection["project_name"],
         username=selection["username"],
      )
      # open events page with filter?
