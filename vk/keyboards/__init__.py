import json

with open("vk/keyboards/texts.json", "r", encoding="utf-8") as f:
    TEXTS = json.load(f)

AUCTION = TEXTS["auction"]
PUBLISHER = TEXTS["publisher"]
BETS = TEXTS["bets"]
COMMISSION = TEXTS["commission"]
BALANCE = TEXTS["balance"]
PAY = TEXTS["pay"]
SWIPE = TEXTS["swipe"]
MANAGEGROUPS = TEXTS["managegroups"]
DIGEST = TEXTS["digest"]
