from typing import List

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


def ensure_hierarchy_template_attrib():
    """Ensure that the HierarchyTemplate attributes are present in the Ayon DB."""

    resp = ayon_api.get("attributes")
    if not resp.status_code == 200:
        raise Exception(f"Failed to get attributes: {resp.content}")

    attributes: List[str] = [attr["name"] for attr in resp.data.get("attributes")]
    if "ashHierarchyTemplate" not in attributes:
        logging.info("Creating HierarchyTemplate Attribute...")
        raise HierarchyTemplateAttributreNotPresent(
            "Please manually create 'ashHierarchyTemplate' Attribute in Ayon."
        )


class HierarchyTemplateProcessor:
    def __init__(self):
        ayon_api.init_service()

    def start_processing(self):
        """Main loop querying AYON events for new `entity.project.created` events"""
        logging.info("Start enrolling for Ayon `entity.project.created` Events...")

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

                # update target event with project name and hierarchy template
                ayon_api.update_event(
                    target_event["id"],
                    project_name=project["name"],
                    # # ? payload doesn't get updated in Ayon
                    # payload={
                    #     "hierarchy_template": project["attrib"]["ashHierarchyTemplate"]
                    # },
                )

                ensure_hierarchy_template_attrib()
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
                success_msg = f"Successfully Created Hierarchy Template {project['attrib']['ashHierarchyTemplate']}"
                logging.info(success_msg)
                ayon_api.update_event(
                    target_event["id"],
                    description=success_msg,
                    status="finished",
                )
