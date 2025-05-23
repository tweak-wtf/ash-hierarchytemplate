name = "hierarchytemplate"
title = "HierarchyTemplate"
version = "0.2.4-dev"

services = {
    "HierarchyTemplateProcessor": {"image": f"doerp/ash-hierarchytemplate-processor:{version}"},
}
client_dir = "ash_hierarchytemplate"

ayon_required_addons = {
    "core": ">=0.3.0",
}
ayon_compatible_addons = {}
