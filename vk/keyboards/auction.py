from . import AUCTION
from vkbottle import Keyboard, KeyboardButtonColor, Text, Callback


creation_methods_kb = Keyboard(inline=True)
creation_methods_kb.add(Callback(AUCTION["poll"], {"auction": "cm:poll"}))
creation_methods_kb.add(Callback(AUCTION["form"], {"auction": "cm:form"}))

confirmation_kb = Keyboard(inline=True)
confirmation_kb.add(Text(AUCTION["confirmation"]))
