from netbox.plugins import PluginMenu, PluginMenuItem

menu = PluginMenu(
    tabs=(
        (
            "CVE Explorer",
            (
                PluginMenuItem(
                    link='plugins:netbox_cvexplorer:cve_list',   # plugins:<app_name>:<url_name>
                    link_text='CVE Übersicht',
                    permissions=['netbox_cvexplorer.view_cve'],   # zeigt sich nur, wenn Recht vorhanden
                ),
            ),
        ),
    )
)