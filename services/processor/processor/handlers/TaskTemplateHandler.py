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
    if not event_folder:
        errmsg = f"Folder with ID {event['summary']['entityId']} not found"
        logging.error(errmsg)
        raise RuntimeError(errmsg)

    logging.info(f"{event_folder = }")
    logging.info(f"{dir(event_folder) = }")

    folder_type_filter = filter(
        lambda tmpl: tmpl["folder_type"] == event_folder["folderType"],
        settings["task_template"],
    )
    template_data = next(folder_type_filter, None)
    if not template_data:
        logging.info("Skipping because no task template matches folder type")
        return

    folder_path_found = False
    for path in event_folder.get("folderPaths", []):
        if path in template_data["folder_paths"]:
            folder_path_found = True
        if not folder_path_found:
            logging.info("Skipping because event folder path doesn't match path filter")
            return

    task_template = TaskTemplate(
        template_data=template_data,
        project=project,
    )
    task_template.apply(folder=event_folder)
