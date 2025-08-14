from . import PUBLISHER
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback


def overlimit_kb(with_other_group: bool):
    overlimit_kb = Keyboard(inline=True)
    overlimit_kb.add(Text(PUBLISHER["same_group"]))
    if with_other_group:
        overlimit_kb.add(Text(PUBLISHER["other_group"]))
    return overlimit_kb
