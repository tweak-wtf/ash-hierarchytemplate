from typing import Any

import ayon_api
from nxtools import logging


class HierarchyTemplateNotFound(Exception):
    pass


class ExistingHierarchyFound(Exception):
    pass


class HierarchyTemplate:
    def __init__(self, project: dict, settings: dict) -> Any:
        self.project = project
        self.settings = settings

    def apply_task(self, task, parent_id):
        logging.info(f"applying task: {task}")
        payload = {
            "name": task["name"],
            "label": task["name"],
            "taskType": task["type"],
            "folderId": parent_id,
        }
        task_resp = ayon_api.post(f"projects/{self.project['name']}/tasks", **payload)
        if not task_resp.status_code == 201:
            raise Exception(f"Failed to create task: {task_resp.content}")

        if task.get("assignees"):
            payload = {
                "mode": "set",
                "users": task["assignees"],
            }
            ayon_api.post(
                f"projects/{self.project['name']}/tasks/{task_resp.data['id']}/assign",
                **payload,
            )

    def create_hierarchy_item(self, item: dict, parent: str = None):
        logging.debug(f"processing {item['name']}:{item['type']}")

        # build payload dict and inject parent item if present
        payload = {
            "name": item["name"],
            "label": item["name"],  # this is important for ShotGrid addon
            "folderType": item["type"],
        }
        if parent:
            payload.update({"parentId": parent})

        # create the item
        resp = ayon_api.post(f"projects/{self.project['name']}/folders", **payload)
        if resp.status_code != 201:
            raise Exception(f"Failed to create item: {resp.content}")

        for task in item["tasks"]:
            self.apply_task(task, resp.data["id"])

        if item.get("children"):
            for child in item["children"]:
                self.create_hierarchy_item(child, parent=resp.data["id"])

    def apply(self) -> None:
        for item in self.settings:
            self.create_hierarchy_item(item)


def process_event(project: dict, settings: dict) -> None:
    # check for existing hierarchy and abort if found
    curr_hierarchy = ayon_api.get_folders_hierarchy(project["name"])
    logging.debug(f"{curr_hierarchy = }")
    if curr_hierarchy.get("hierarchy"):
        raise ExistingHierarchyFound(
            f"Please clear the hierarchy for project '{project['name']}'."
        )

    # check if the Hierarchy Template is valid
    project_template_key = project["attrib"]["ashHierarchyTemplate"]
    templates = [t for t in settings["hierarchy_template"]]
    template_keys = [t["name"] for t in templates]
    if project_template_key not in template_keys:
        raise HierarchyTemplateNotFound(
            f"'{project_template_key}' not a valid Hierarchy Template key."
        )

    # build the Hierarchy Template
    template_settings = [
        t["hierarchy"] for t in templates if t["name"] == project_template_key
    ][0]
    template = HierarchyTemplate(project, template_settings)
    template.apply()
