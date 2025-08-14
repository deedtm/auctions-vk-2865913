import json


def get_commands(path: str = "vk/bot/handlers/commands.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_command(literal: str, path: str = "vk/bot/handlers/commands.json") -> dict:
    commands = get_commands(path)
    for d in commands:
        if literal in d["literals"]:
            return d


def get_required_args(command: dict) -> bool:
    if "args" not in command:
        return []
    return list(filter(lambda a: a[0] == "{" and a[-1] == "}", command["args"]))


def separate_args(command: str) -> tuple[str, list[str]]:
    literal, args = command.split(maxsplit=1) if " " in command else (command, "")
    args = args.strip().split()
    return literal, args
