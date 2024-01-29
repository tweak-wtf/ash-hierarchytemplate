from typing import Type
from .version import __version__
from .settings import HierarchyTemplateAddonSettings, DEFAULT_VALUES

from ayon_server.addons import BaseServerAddon
# from ayon_server.api.dependencies import dep_current_user, dep_project_name


class HierarchyTemplateAddon(BaseServerAddon):
    name = "HierarchyTemplate"
    title = "Hierarchy Template"
    version = __version__
    settings_model: Type[
        HierarchyTemplateAddonSettings
    ] = HierarchyTemplateAddonSettings

    # frontend_scopes: dict[str, Any] = {"settings": {}}

    # this variable actually exposes theese services to the webui
    services = {
        "HierarchyTemplateProcessor": {
            "image": f"doerp/ash-hierarchytemplate-processor:{version}",
        },
    }

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)
