import json


def load_template(template_name):
    with open(f"templates/{template_name}.json", "r", encoding="utf-8") as file:
        return json.load(file)


COMMANDS = load_template("commands")
