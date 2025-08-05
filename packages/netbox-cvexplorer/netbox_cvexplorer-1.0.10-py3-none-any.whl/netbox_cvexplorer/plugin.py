from netbox.plugins import PluginConfig
import json
from importlib.metadata import metadata
from pathlib import Path

# Informationen aus JSON laden
here = Path(__file__).parent.resolve()
with open(f"{here}/info.json", "r") as pluginvarsfile:
    pluginvars = json.load(pluginvarsfile)
    for pluginvar in pluginvars:
        locals()[f"{pluginvar}"]=pluginvars[pluginvar]

class CVExplorerConfig(PluginConfig):
    name = __name__
    verbose_name = __verbose_name__
    version = __version__
    description = __description__
    author = __author__
    author_email = __author_email__
    base_url = __base_url__
    version = '1.0.6'
    min_version = '4.0'
    required_settings = []
    default_settings = {
        'loud': False
    }
    caching_config = {
        '*': None
    }

config = CVExplorerConfig