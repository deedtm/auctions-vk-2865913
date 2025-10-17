import os

from . import _config

INFO_ACCESS = _config.getint("admin", "info_commands_access_level")
SET_ACCESS = _config.getint("admin", "set_commands_access_level")
BAN_ACCESS = _config.getint("admin", "ban_access_level")
ADMIN_ACCESS = _config.getint("admin", "admin_access_level")
MODERATOR_ACCESS = _config.getint("admin", "moderator_access_level")
EXPORT_DIRECTORY = _config.get("admin", "export_directory")

ADMINS_IDS = list(map(int, os.getenv('ADMINS_IDS').split()))
MODERATORS_IDS = list(map(int, os.getenv('MODERATORS_IDS').split()))
