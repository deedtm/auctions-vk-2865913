from vkbottle import GroupTypes
from vkbottle.dispatch.rules import ABCRule

from config.vk import REDEMPTION_COMMAND
from database.lots.utils import is_ongoing_auction


class AuctionBetFilter(ABCRule[GroupTypes.WallReplyNew]):
    async def check(self, event: GroupTypes.WallReplyNew) -> bool:
        o = event.object

        if o.is_from_post_author:
            return False

        if not (o.text.isnumeric() or REDEMPTION_COMMAND in o.text.lower()):
            return False

        is_ongoing = await is_ongoing_auction(o.post_owner_id, o.post_id)
        if not is_ongoing:
            return False

        return True
