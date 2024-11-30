from typing import Dict, List

import ayon_api
from time import sleep
from os import environ as env
from nxtools import logging, log_traceback
from socket import gethostname as get_hostname

from .handlers import HierarchyTemplateHandler

# set logging user to service name
if service_name := env.get("AYON_SERVICE_NAME"):
    logging.user = service_name


class HierarchyTemplateAttributreNotPresent(Exception):
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
    if "ashHierarchyTemplate" not in attributes:
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
    else:  # check if all templates are present
        attrib_enum = [
            attr
            for attr in resp.data.get("attributes")
            if attr["name"] == "ashHierarchyTemplate"
        ][0]["data"]["enum"]
        attrib_enum_names = {tmpl["value"] for tmpl in attrib_enum}
        new_attrib_enum_names = {
            tmpl["name"] for tmpl in settings["hierarchy_template"]
        }
        if not new_attrib_enum_names.issubset(attrib_enum_names):
            missing_templates = new_attrib_enum_names - attrib_enum_names
            raise HierarchyTemplateAttributreNotPresent(
                f"Please add the following templates to 'ashHierarchyTemplate' Attribute: {missing_templates}"
            )


class HierarchyTemplateProcessor:
    def __init__(self):
        ayon_api.init_service()

    def start_processing(self):
        """Main loop querying AYON events for new `entity.project.created` events"""
        logging.info("Start enrolling for Ayon `entity.project.created` Events...")
        self.settings = ayon_api.get_service_addon_settings()
        ensure_hierarchy_template_attrib(self.settings)

        while True:
            target_event = ayon_api.enroll_event_job(
                source_topic="entity.project.created",
                target_topic="hierarchyTemplate.create",
                description="Create Hierarchy Template",
                sender=get_hostname(),
                max_retries=3,
                sequential=False,
            )

            if not target_event:
                sleep(5)
                continue

            try:
                self.settings = ayon_api.get_service_addon_settings()
                logging.info(f"Processing Event: {target_event['id']}")

                # query source event and its project
                source_event = ayon_api.get_event(target_event["dependsOn"])
                project = ayon_api.get_project(source_event["project"])
                if not project:
                    raise Exception(f"Project '{source_event['project']}' not found.")

                if "aysvc" in source_event["sender"]:
                    raise Exception("Event is from AYON Service, skipping...")

                ayon_api.update_event(
                    target_event["id"],
                    project_name=project["name"],
                )

                ensure_hierarchy_template_attrib(self.settings)
                if not project["attrib"].get("ashHierarchyTemplate"):
                    raise HierarchyTemplateAttributreNotPresent(
                        "Please set 'ashHierarchyTemplate' Attribute on this project."
                    )

                # process target event
                HierarchyTemplateHandler.process_event(project, self.settings)
            except Exception as err:
                log_traceback(err)
                ayon_api.update_event(
                    target_event["id"],
                    description=f"{err}",
                    status="failed",
                )
            else:
                success_msg = "Successfully applied Template"
                logging.info(success_msg)
                ayon_api.update_event(
                    target_event["id"],
                    description=success_msg,
                    status="finished",
                )
