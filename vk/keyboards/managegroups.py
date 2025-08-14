from vkbottle import Callback, Keyboard

from . import MANAGEGROUPS

main_menu_kb = Keyboard(inline=True)
main_menu_kb.add(
    Callback(MANAGEGROUPS["set_waterfalls"], {"managegroups": "set:waterfalls"})
)
main_menu_kb.row()
main_menu_kb.add(
    Callback(MANAGEGROUPS["set_commissions"], {"managegroups": "set:commissions"})
)
main_menu_kb.row()
main_menu_kb.add(
    Callback(
        MANAGEGROUPS["set_auctions_template"], {"managegroups": "set:auctions_template"}
    )
)

templates_menu_kb = Keyboard(inline=True)
templates_menu_kb.add(
    Callback(MANAGEGROUPS["templates_menu"]["edit"], {"managegroups": "templates:edit"})
)
