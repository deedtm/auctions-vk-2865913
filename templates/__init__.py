import json


def load_template(template_name):
    with open(f"templates/{template_name}.json", "r", encoding="utf-8") as file:
        return json.load(file)


COMMANDS = load_template("commands")
ERRORS = load_template("errors")
MODERATION = load_template("moderation")
BETS = load_template("bets")
PUBLISH = load_template("publish")
PAY = load_template("pay")
COLLECTOR = load_template("collector")
ADMIN_COMMANDS = load_template("admin_commands")
LOYAL_NOTIFICATIONS = load_template("loyal_notifications")
DIGEST = load_template("digest")
