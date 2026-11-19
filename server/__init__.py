from ayon_server.addons import BaseServerAddon
from ayon_server.logging import log_traceback, logger
from ayon_server.api.dependencies import CurrentUser
from ayon_server.types import OPModel
from ayon_server.operations import ProjectLevelOperations


from pydantic import BaseModel

# import ayon_api
# from ayon_api.entity_hub import EntityHub

from .settings import HierarchyTemplateAddonSettings, DEFAULT_VALUES
# from ayon_server.api.dependencies import dep_current_user, dep_project_name


class ApplyTemplateModel(BaseModel):
    projectName: str
    templateName: str
    folderIds: list[str]
    selectedTemplate: dict


class HierarchyTemplateAddon(BaseServerAddon):
    settings_model: type[HierarchyTemplateAddonSettings] = HierarchyTemplateAddonSettings
    addon_type = "server"

    frontend_modules = {"hierarchytemplates": ["manifest"]}

    def initialize(self):
        self.add_endpoint(
            "/task-templates/{project_name}",
            self.get_task_templates,
            method="GET",
            description="Lists applicable task templates",
        )
        self.add_endpoint(
            "/apply-task-template",
            self.apply_task_template,
            method="POST",
            description="Applies a task template to selected folder(s)",
        )

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)

    async def get_task_templates(self, project_name: str) -> list:
        project_settings = await self.get_project_settings(project_name)
        logger.debug(f"{project_settings = }")

        if not project_settings.task_templates:
            logger.error("No task templates found.")
            return []

        return project_settings.task_templates

    async def apply_task_template(self, payload: ApplyTemplateModel):
        logger.info(f"{payload = }")
        project_name = payload.projectName
        template_name = payload.templateName
        folders = payload.folderIds
        selected_template = payload.selectedTemplate

        pops = ProjectLevelOperations(project_name)
        logger.debug(f"{pops = }")

        for folder_id in folders:
            logger.debug(f"Processing folder: {folder_id}")
            for task in selected_template.get("tasks", []):
                logger.debug(f"Processing task: {task}")
                pops.create(
                    "task",
                    folder_id=folder_id,
                    name=task["name"],
                    # label=task.get("label"),  # check again with SG
                    task_type=task["type"],
                    # as_user
                )
        result = await pops.process(can_fail=True, raise_on_error=False)
        return result



