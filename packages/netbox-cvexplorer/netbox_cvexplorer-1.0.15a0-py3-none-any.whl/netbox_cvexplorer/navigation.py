from django.conf import settings
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem, PluginMenuGroup

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_cvexplorer:cve_list',
        link_text='CVE Übersicht',
        permissions=['netbox_cvexplorer.view_cve']
    ),
)

menu = PluginMenu(
    label='CVE Explorer',
    groups=(
        PluginMenuGroup(
            label='Übersicht',
            items=menu_items
        ),
    )
)
