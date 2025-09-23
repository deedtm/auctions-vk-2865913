from . import PUBLISHER
from vkbottle import Keyboard, Callback


def overlimit_kb(with_other_group: bool, group_id: int):
    overlimit_kb = Keyboard(inline=True)
    overlimit_kb.add(Callback(PUBLISHER["same_group"], {"overlimited": "same_group"}))
    if with_other_group and group_id:
        overlimit_kb.add(Callback(PUBLISHER["other_group"], {"overlimited": f"{group_id}_group"}))
    return overlimit_kb
