NUMBERS_EMOJIS = "0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"


def int_to_emojis(number: int) -> str:
    return "".join([NUMBERS_EMOJIS[int(i)] for i in str(number)])
