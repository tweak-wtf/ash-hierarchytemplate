from pathlib import Path

from ayon_core.addon import AYONAddon, IPluginPaths

from .version import __version__


ADDON_ROOT = Path(__file__).resolve().parent
ADDON_NAME = "hierarchytemplate"


class HierarchyTemplateAddon(AYONAddon, IPluginPaths):
    label = "Hierarchy Template"
    name = ADDON_NAME
    version = __version__

    def initialize(self, settings):
        self.enabled = True
        self.settings = settings

    def get_plugin_paths(self):
        return {
            "actions": [
                str(ADDON_ROOT / "plugins" / "actions"),
            ],
        }
