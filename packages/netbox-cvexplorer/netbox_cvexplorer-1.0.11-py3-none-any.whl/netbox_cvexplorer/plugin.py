from netbox.plugins import PluginConfig
from importlib.metadata import metadata
from pathlib import Path

plugin = metadata('netbox_cvexplorer')

class CVExplorerConfig(PluginConfig):
    name = plugin.get('Name').replace('-', '_')
    verbose_name = plugin.get('Name').replace('-', ' ').title()
    version = plugin.get('Version')
    description = plugin.get('Summary')
    author = plugin.get('Author')
    author_email = plugin.get('Author-email')
    base_url = "netbox_cvexplorer"
    min_version = '4.0'
    required_settings = []
    default_settings = {
        'loud': False
    }
    caching_config = {
        '*': None
    }

config = CVExplorerConfig