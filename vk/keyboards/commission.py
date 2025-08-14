from . import COMMISSION
from vkbottle import Keyboard, Text


commission_main_kb = Keyboard(inline=True)
commission_main_kb.add(Text(COMMISSION["pay_all"]))
commission_main_kb.add(Text(COMMISSION["pay_partially"]))
