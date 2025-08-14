from . import PAY
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback


update_kb = Keyboard(inline=True)
update_kb.add(Callback(PAY["update"], payload={"pay": "update"}))
