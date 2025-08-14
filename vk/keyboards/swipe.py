from vkbottle import Callback, Keyboard, KeyboardButtonColor, Text

from . import SWIPE


def swipe_kb(
    payload_key: str, offset: int, last_index: int, payload_value: str = "swipe"
):
    kb = Keyboard(inline=True)

    swipe_buttons = []

    if offset != 0:
        swipe_buttons.append((SWIPE["previous"], offset - 1))
    if offset != last_index:
        swipe_buttons.append((SWIPE["next"], offset + 1))

    for tmpl, arg in swipe_buttons:
        pl = {payload_key: f"{payload_value}:{arg}"}
        kb.add(Callback(tmpl, pl))

    kb.row()
    kb.add(
        Text(SWIPE["page"].format(offset + 1, last_index + 1)),
        KeyboardButtonColor.PRIMARY,
    )
    return kb
