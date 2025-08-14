from . import BALANCE
from vkbottle import Keyboard, Callback

main_menu_kb = Keyboard(inline=True)
main_menu_kb.add(Callback(BALANCE["top_up"], {"balance": "top_up"}))
main_menu_kb.add(Callback(BALANCE["history"], {"balance": "history"}))

