from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="CVExplorer",
    icon_class="mdi mdi-security",
    groups=(
        (
            "",
            (
                PluginMenuItem(
                    link="plugins:netbox_cvexplorer:cve_list",
                    link_text="CVE Liste",
                    permissions=["netbox_cvexplorer.view_cve"],
                ),
            ),
        ),
    ),
)