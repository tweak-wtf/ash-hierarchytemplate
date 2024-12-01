from typing import List, Optional

from pydantic import Field
from ayon_server.settings import BaseSettingsModel
from ayon_server.settings.enum import task_types_enum, folder_types_enum

from ayon_server.lib.postgres import Postgres


async def active_users_enum():
    query = "SELECT * FROM users WHERE active = TRUE"
    users = await Postgres.fetch(query)
    return list([user["name"] for user in users])


class Task(BaseSettingsModel):
    name: str = Field("Name", description="Name of the Task.")
    type: str = Field(
        "Generic",
        enum_resolver=task_types_enum,
        title="Task Type",
        scope=["studio"],
    )
    assignees: List[str] = Field(
        default="",
        enum_resolver=active_users_enum,
        description="List of Assignees.",
        title="Assignees",
    )


class HierarchyItem(BaseSettingsModel):
    """Hierarchy Item Settings."""

    _layout = "expanded"

    name: str = Field("folder", description="Name of the Hierarchy Item.")
    type: str = Field(
        "Folder",
        enum_resolver=folder_types_enum,
        title="Item Type",
        scope=["studio"],
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="List of Tasks.",
        title="Tasks",
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


class TaskTemplateSettings(BaseSettingsModel):
    """Task Template Settings."""

    name: str = Field("", description="Name of the Task Template Filter.")
    folder_paths: List[str] = Field(
        default_factory=list,
        description="List of Folder Paths.",
        title="Folder Paths",
    )
    folder_type: str = Field(
        default_factory=list,
        enum_resolver=folder_types_enum,
        title="Folder Type",
        scope=["studio"],
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="List of Tasks.",
        title="Tasks",
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.name = self.folder_type.lower()


class HierarchyTemplateAddonSettings(BaseSettingsModel):
    """Hierarchy Template Addon Settings."""

    task_template: List[TaskTemplateSettings] = Field(
        default_factory=list,
        description="List of Task Templates.",
        title="Task Templates",
    )
    hierarchy_template: List[HierarchyTemplateSettings] = Field(
        default_factory=list,
        description="List of Project Hierarchy Templates.",
        title="Hierarchy Templates",
    )


DEFAULT_VALUES = {
    "hierarchy_template": [
        {
            "name": "default",
            "hierarchy": [
                {
                    "name": "assets",
                    "type": "Folder",
                    "tasks": [],
                    "children": [
                        {
                            "name": "testAsset01",
                            "type": "Asset",
                            "tasks": [
                                {"name": "modeling", "type": "Modeling"},
                                {"name": "texture", "type": "Texture"},
                                {"name": "rigging", "type": "Rigging"},
                            ],
                            "children": [],
                        }
                    ],
                },
                {
                    "name": "shots",
                    "type": "Folder",
                    "tasks": [{"name": "edit", "type": "Edit"}],
                    "children": [
                        {
                            "name": "testShot01",
                            "type": "Shot",
                            "tasks": [
                                {"name": "compositing", "type": "Compositing"},
                                {"name": "animation", "type": "Animation"},
                            ],
                            "children": [],
                        }
                    ],
                },
            ],
        }
    ]
}
