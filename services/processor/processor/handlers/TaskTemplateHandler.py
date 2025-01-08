from typing import Any, Dict

import ayon_api
from nxtools import logging


class TaskTemplate:
    def __init__(self, template_data: Dict, project: Dict) -> None:
        self.project = project
        self.tasks = template_data.get("tasks")
        self.folder_type = template_data.get("folder_type")
        self.folder_paths = template_data.get("folder_paths")

    def apply(self, folder) -> None:
        for task in self.tasks:
            payload = {
                "name": task["name"],
                "label": task["name"],
                "taskType": task["type"],
                "folderId": folder["id"],
            }
            task_resp = ayon_api.post(
                f"projects/{self.project['name']}/tasks", **payload
            )
            if task_resp.status_code != 201:
                logging.error(f"Failed to create task: {task_resp.data}")
                continue

            if task.get("assignees"):
                payload = {
                    "mode": "set",
                    "users": task["assignees"],
                }
                ayon_api.post(
                    f"projects/{self.project['name']}/tasks/{task_resp.data['id']}/assign",
                    **payload,
                )


def process_event(event: dict, settings: dict, project: dict) -> None:
    logging.info(f"{event = }")
    logging.info(f"{settings = }")
    event_folder = ayon_api.get_folder_by_id(
        project["name"], event["summary"]["entityId"]
    )
    logging.info(f"{event_folder = }")
    logging.info(f"{dir(event_folder) = }")

    if template_filter_hit := filter(
        lambda tmpl: tmpl["folder_type"] == event_folder["folderType"],
        settings["task_template"],
    ):
        if path_filter_hit := filter(
            lambda tmpl: event_folder["path"] in tmpl["folder_paths"]
            if tmpl["folder_paths"]
            else True,
            template_filter_hit,
        ):
            task_template = TaskTemplate(
                template_data=next(path_filter_hit),
                project=project,
            )
            task_template.apply(folder=event_folder)
