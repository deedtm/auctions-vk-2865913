from vkbottle import Callback, Keyboard

from . import DIGEST

main_menu_kb = Keyboard(inline=True)
main_menu_kb.add(Callback(DIGEST["edit_pin"], {"digest": "edit_pin"}))
main_menu_kb.add(Callback(DIGEST["edit_pic"], {"digest": "edit_pic"}))
