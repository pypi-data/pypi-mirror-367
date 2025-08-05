from django.conf import settings
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

plugin_settings = settings.PLUGINS_CONFIG["netbox_cvexplorer"]

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


if plugin_settings.get("top_level_menu"):
    menu = PluginMenu(
        label="CVExplorer",
        groups=(
            (
                "Access Lists",
                (accesslist_item,),
            )
        ),
        icon_class="mdi mdi-lock",
    )
else:
    menu_items = (
        accesslist_item,
    )