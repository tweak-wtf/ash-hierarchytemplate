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
              "taskType": task["type"],
              "folderId": folder["id"],
            }
            ayon_api.post(f"projects/{self.project['name']}/tasks", **payload)


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
