import json

def get_commands():
    with open("vk/handlers/commands.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_command(literal: str):
    commands = get_commands()
    for d in commands:
        if literal in d["literals"]:
            return d
