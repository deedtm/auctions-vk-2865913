from . import PUBLISHER
from vkbottle import Keyboard, Callback


def overlimit_kb(with_other_group: bool):
    overlimit_kb = Keyboard(inline=True)
    overlimit_kb.add(Callback(PUBLISHER["same_group"], {"overlimited": "same_group"}))
    if with_other_group:
        overlimit_kb.add(Callback(PUBLISHER["other_group"], {"overlimited": "other_group"}))
    return overlimit_kb
