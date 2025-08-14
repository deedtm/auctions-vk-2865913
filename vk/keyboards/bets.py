from . import BETS
from vkbottle import Keyboard, Text


seller_notification_kb = Keyboard(inline=True)
seller_notification_kb.add(Text(BETS["seller_notification"]))
