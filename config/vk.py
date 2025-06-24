from . import _config

_prefixes = _config.get("vk", "default_prefixes")
DEFAULT_PREFIXES = _prefixes.split(",")
