from ..__utils import get_command as gc
from ..__utils import get_commands as gcs
from ..__utils import get_required_args, separate_args

PATH = "vk/bot/handlers/admin/commands.json"


def get_commands(separate_by_types: bool = False) -> dict:
    if not separate_by_types:
        return gcs(PATH)
    commands = gcs(PATH)
    separated = {}
    for command in commands:
        separated[command["type"]] = command
    return separated


def get_command(literal: str) -> dict:
    return gc(literal, PATH)
