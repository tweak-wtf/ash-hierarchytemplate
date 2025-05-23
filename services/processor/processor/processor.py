from typing import Dict, List

import ayon_api
from time import sleep
from os import environ as env
from nxtools import logging, log_traceback
from socket import gethostname as get_hostname

from .handlers import HierarchyTemplateHandler, TaskTemplateHandler

# set logging user to service name
if service_name := env.get("AYON_SERVICE_NAME"):
    logging.user = service_name


class HierarchyTemplateAttributreNotPresent(Exception):
    pass


class KnownException(Exception):
    pass


def ensure_hierarchy_template_attrib(settings: Dict):
    """Ensure that the HierarchyTemplate attributes are present in the Ayon DB."""
    resp = ayon_api.get("attributes")
    if not resp.status_code == 200:
        raise Exception(f"Failed to get attributes: {resp.content}")

    attributes: List[str] = [attr["name"] for attr in resp.data.get("attributes")]
    new_attrib_enum = [
        {
            "value": tmpl["name"],
            "label": tmpl["name"].capitalize().replace("_", " "),
        }
        for tmpl in settings["hierarchy_template"]
    ]

    # service attribute found
    # check if all templates are present
    if filter_match := filter(
        lambda attr: attr["name"] == "ashHierarchyTemplate",
        resp.data.get("attributes"),
    ):
        attrib_enum = next(filter_match)["data"]["enum"]
        attrib_enum_names = {tmpl["value"] for tmpl in attrib_enum}
        new_attrib_enum_names = {
            tmpl["name"] for tmpl in settings["hierarchy_template"]
        }
        if not new_attrib_enum_names.issubset(attrib_enum_names):
            missing_templates = new_attrib_enum_names - attrib_enum_names
            raise HierarchyTemplateAttributreNotPresent(
                f"Please add the following templates to 'ashHierarchyTemplate' Attribute: {missing_templates}"
            )
    else:  # create the attribute
        new_attrib_position = len(attributes) + 1
        new_attrib_data = {
            "type": "string",
            "title": "Hierarchy Template",
            "description": "Hierarchy Template Name",
            "default": "",  # enable maybe?
            "enum": new_attrib_enum,
        }
        ayon_api.set_attribute_config(
            attribute_name="ashHierarchyTemplate",
            data=new_attrib_data,
            position=new_attrib_position,
            scope=["project"],
        )


class HierarchyTemplateProcessor:
    def __init__(self):
        ayon_api.init_service()

    def start_processing(self):
        """Main loop querying AYON events for new `entity.project.created` and `entity.folder.created` events"""
        self.settings = ayon_api.get_service_addon_settings()
        ensure_hierarchy_template_attrib(self.settings)

        while True:
            project_hierarchy_event = ayon_api.enroll_event_job(
                source_topic="entity.project.created",
                target_topic="hierarchyTemplate.create",
                description="Create Hierarchy Template",
                sender=get_hostname(),
                max_retries=1,
                sequential=False,
            )
            folder_tasks_event = ayon_api.enroll_event_job(
                source_topic="entity.folder.created",
                target_topic="taskTemplate.create",
                description="Create Hierarchy Template",
                sender=get_hostname(),
                max_retries=1,
                sequential=False,
                events_filter={
                    "operator": "or",
                    "conditions": [
                        {   # don't ignore events from API calls
                            "key": "sender",
                            "operator": "notnull",
                        },
                        {   # don't ignore events from all ASH services
                            "key": "sender",
                            "operator": "notin",
                            "value": "aysvc",
                        },
                    ],
                },
            )
            target_event = project_hierarchy_event or folder_tasks_event

            if not target_event:
                sleep(5)
                continue

            try:
                self.settings = ayon_api.get_service_addon_settings()
                logging.info(f"Processing Event: {target_event['id']}")

                # query target and source event and its project
                target_event = ayon_api.get_event(target_event["id"])
                source_event = ayon_api.get_event(target_event["dependsOn"])
                logging.debug(f"{target_event = }")
                logging.debug(f"{source_event = }")
                project = ayon_api.get_project(source_event["project"])
                if not project:
                    errmsg = f"Project '{source_event['project']}' not found."
                    raise RuntimeError(errmsg)

                if not source_event.get("sender"):
                    raise KnownException("Source Event has no sender.")

                if "aysvc" in source_event["sender"]:
                    logging.debug(f"{source_event['sender'] = }")
                    raise KnownException("Event is from AYON Service.")

                ayon_api.update_event(
                    target_event["id"],
                    project_name=project["name"],
                )

                ensure_hierarchy_template_attrib(self.settings)

                # process target event
                if target_event["topic"] == "hierarchyTemplate.create":
                    if not project["attrib"].get("ashHierarchyTemplate"):
                        raise HierarchyTemplateAttributreNotPresent(
                            "Please set 'ashHierarchyTemplate' Attribute on this project."
                        )
                    HierarchyTemplateHandler.process_event(project, self.settings)
                if target_event["topic"] == "taskTemplate.create":
                    TaskTemplateHandler.process_event(
                        source_event, self.settings, project
                    )
            except (RuntimeError, HierarchyTemplateAttributreNotPresent) as err:
                log_traceback(err)
                ayon_api.update_event(
                    target_event["id"],
                    description=f"{err}",
                    status="failed",
                )
            except KnownException as err:
                logging.debug(f"{err}")
                ayon_api.update_event(
                    target_event["id"],
                    description=f"{err}",
                    status="finished",
                )
            else:
                success_msg = "Successfully applied Template"
                logging.info(success_msg)
                ayon_api.update_event(
                    target_event["id"],
                    description=success_msg,
                    status="finished",
                )
