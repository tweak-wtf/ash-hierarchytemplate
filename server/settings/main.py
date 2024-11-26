from typing import List, Optional

from pydantic import Field
from ayon_server.settings import BaseSettingsModel
from ayon_server.settings.enum import task_types_enum, folder_types_enum


class Task(BaseSettingsModel):
    name: str = Field("Name", description="Name of the Task.")
    type: str = Field(
        "Generic",
        enum_resolver=task_types_enum,
        title="Task Type",
        scope=["studio"],
    )


class TaskTemplate(BaseSettingsModel):
    """Task Template Settings."""

    # name: str = Field("Apply Tasks", description="Applies all Tasks to Parent Item.")
    enabled: bool = Field(
        False,
        description="Whether the following Tasks shall be created or not.",
        title="Enabled",
    )
    tasks: List[Task] = Field(
        default_factory=list,
        # description="List of Tasks.",
        # title="Tasks",
    )


class HierarchyItem(BaseSettingsModel):
    """Hierarchy Item Settings."""

    # _layout = "expanded"

    name: str = Field("folder", description="Name of the Hierarchy Item.")
    enabled: bool = Field(
        True,
        description="Whether this Hierarchy Item is enabled.",
        title="Enabled",
    )
    type: str = Field(
        "Folder",
        enum_resolver=folder_types_enum,
        title="Item Type",
        scope=["studio"],
    )
    task_template: Optional[TaskTemplate] = Field(
        None,
        description="Task Template to use for this item.",
        title="Task Template",
    )
    children: List["HierarchyItem"] = Field(
        default_factory=list,
        description="List of Hierarchy Items.",
        title="Children",
    )


class HierarchyTemplateSettings(BaseSettingsModel):
    """Hierarchy Template Settings."""

    name: str = Field(
        "HierarchyTemplate", description="Name of the Hierarchy Template."
    )
    hierarchy: List[HierarchyItem] = Field(
        default_factory=list,
        description="Hierarchy Structure.",
        title="Hierarchy",
    )


class HierarchyTemplateAddonSettings(BaseSettingsModel):
    """Hierarchy Template Addon Settings."""

    hierarchy_template: List[HierarchyTemplateSettings] = Field(
        default_factory=list,
        description="List of Hierarchy Template Settings.",
        title="Templates",
    )


DEFAULT_VALUES = {
    "hierarchy_template": [
        {
            "name": "basic",
            "hierarchy": [
                {
                    "name": "sequences",
                    "type": "Folder",
                    "enabled": True,
                    "children": [
                        {
                            "name": "main",
                            "type": "Sequence",
                            "enabled": True,
                            "children": [],
                            "task_template": {
                                "tasks": [
                                    {"name": "ingest", "type": "Edit"},
                                    {"name": "daily", "type": "Edit"},
                                ],
                                "enabled": True,
                            },
                        }
                    ],
                    "task_template": {"tasks": [], "enabled": False},
                },
                {
                    "name": "assets",
                    "type": "Folder",
                    "enabled": True,
                    "children": [
                        {
                            "name": "environment",
                            "type": "Folder",
                            "enabled": True,
                            "children": [],
                            "task_template": {"tasks": [], "enabled": False},
                        },
                        {
                            "name": "character",
                            "type": "Folder",
                            "enabled": True,
                            "children": [],
                            "task_template": {"tasks": [], "enabled": False},
                        },
                        {
                            "name": "prop",
                            "type": "Folder",
                            "enabled": True,
                            "children": [],
                            "task_template": {"tasks": [], "enabled": False},
                        },
                    ],
                    "task_template": {"tasks": [], "enabled": False},
                },
            ],
        }
    ]
}
