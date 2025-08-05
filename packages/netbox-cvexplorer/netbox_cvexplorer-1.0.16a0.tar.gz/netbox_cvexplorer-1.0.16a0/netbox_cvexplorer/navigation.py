from django.conf import settings
from netbox.plugins import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_cvexplorer:cve_list',
        link_text='CVE Übersicht',
        permissions=['netbox_cvexplorer.view_cve'],
    ),
)
