from vkbottle import BaseStateGroup


class AuctionCreating(BaseStateGroup):
    FORM_INPUT = "form_input"
    POLL_INPUT = "poll_input"
    CONFIRMATION = "confirmation"
