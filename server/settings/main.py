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
        default_factory=list,
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


class AutoApplySettingsModel(BaseSettingsModel):
    """Auto Apply Settings."""

    enabled: bool = Field(
        False,
        description="Enable auto apply for this task template.",
        title="Auto Apply",
    )
    folder_types: list[str] = Field(
        default_factory=list,
        enum_resolver=folder_types_enum,
        description="List of Folder Types for auto apply.",
        title="Folder Types",
    )
    folder_paths: list[str] = Field(
        default_factory=list,
        description="List of Folder Paths.",
        title="Folder Paths",
    )


class TaskTemplateSettings(BaseSettingsModel):
    """Task Template Settings."""

    name: str = Field("", description="Name of the Task Template.")
    tasks: list[Task] = Field(
        default_factory=list,
        description="List of Tasks.",
        title="Tasks",
    )
    auto_apply: AutoApplySettingsModel = AutoApplySettingsModel(
        default_factory=AutoApplySettingsModel,
        title="Auto Apply",
        description="Auto Apply Settings.",
    )


class HierarchyTemplateAddonSettings(BaseSettingsModel):
    """Hierarchy Template Addon Settings."""

    task_templates: List[TaskTemplateSettings] = Field(
        default_factory=list,
        description="List of Task Templates.",
        title="Task Templates",
    )
    project_templates: List[HierarchyTemplateSettings] = Field(
        default_factory=list,
        description="List of Project Hierarchy Templates.",
        title="Hierarchy Templates",
    )


# todo: create sane defaults
DEFAULT_VALUES = {}
