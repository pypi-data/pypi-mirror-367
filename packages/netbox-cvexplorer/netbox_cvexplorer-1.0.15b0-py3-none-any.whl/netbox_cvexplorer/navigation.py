from django.conf import settings
from netbox.plugins import PluginMenuItem, PluginMenu

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_cvexplorer_clean:cve_list',
        link_text='CVE Übersicht',
        permissions=['netbox_cvexplorer_clean.view_cve'],
        buttons=[]
    ),
)

menu = PluginMenu(
    label='CVE Explorer',
    items=menu_items
)
