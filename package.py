name = "hierarchytemplate"
title = "HierarchyTemplate"
version = "0.2.0-dev"

services = {
    "processor": {"image": f"doerp/ash-hierarchytemplate:{version}"},
}
client_dir = "ash_hierarchytemplate"

ayon_required_addons = {
    "core": ">=0.3.0",
}
ayon_compatible_addons = {}
