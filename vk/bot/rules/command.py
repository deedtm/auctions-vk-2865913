import re

from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule

from config.vk import DEFAULT_PREFIXES
from templates import ERRORS


class CommandFilter(ABCRule[Message]):
    def __init__(
        self,
        literals,
        prefixes=DEFAULT_PREFIXES,
        args=[],
        required_args=[],
        args_sep=" ",
    ):
        self.literals = literals
        self.prefixes = prefixes
        self.args = args
        self.required_args = required_args
        self.args_count = len(required_args)
        self.args_sep = args_sep

        is_empty_prefix = " " in prefixes
        escaped_prefixes = [re.escape(prefix) for prefix in prefixes if prefix != " "]
        prefixes_pattern = "|".join(escaped_prefixes)
        if is_empty_prefix:
            prefixes_pattern = f"(?:{prefixes_pattern}|\\s*)"

        literals_pattern = "|".join([re.escape(literal) for literal in literals])

        self.command_pattern = re.compile(rf"^({prefixes_pattern})({literals_pattern})")

    async def check(self, e: Message) -> bool:
        if not self.command_pattern.match(e.text.lower()):
            return False

        if self.args_count > 0:
            args = e.text.split(self.args_sep)
            if len(args) < self.args_count + 1:
                tmpl = ERRORS["not_enough_args"]
                text = tmpl.format(", ".join(self.required_args))
                await e.answer(text)
                return False

        return True
