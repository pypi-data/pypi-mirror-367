from django.conf import settings
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

# Access List
accesslist_item = PluginMenuItem(
    link="plugins:netbox_cvexplorer:cve_list",
    link_text="Access Lists",
    permissions=[],
    buttons=(
        PluginMenuButton(
            link="plugins:netbox_cvexplorer:cve_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=[],
        ),
    ),
)

menu_items = (
    accesslist_item,
)