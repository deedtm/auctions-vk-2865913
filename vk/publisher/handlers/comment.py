import time

from vkbottle import GroupEventType, GroupTypes

from database.lots.utils import get_lot, update_lot_data
from enums.moderation import LotStatusDB
from templates import BETS

from ..config import labeler, logger, user_api
from ..rules.auction_bet import AuctionBetFilter
from ..utils import edit_post


@labeler.raw_event(
    GroupEventType.WALL_REPLY_NEW, GroupTypes.WallReplyNew, AuctionBetFilter()
)
async def wall_reply_new(event: GroupTypes.WallReplyNew):
    o = event.object
    w = event.ctx_api.wall

    bet = int(o.text)
    lot = await get_lot(group_id=o.post_owner_id, post_id=o.post_id)

    mn_start_bet = lot.start_price # + lot.step_price
    mn_new_bet = max((lot.last_bet or 0) + lot.step_price, mn_start_bet)

    last_bettor_text = None
    to_update_post, to_update_lot = False, False
    update_kwargs = {
        "last_bet": bet,
        "last_bet_comment": o.id,
        "last_bet_date": int(time.time()),
        "last_bettor_id": o.from_id,
    }

    if bet < mn_start_bet:
        template = BETS["lt_start"]
        args = (lot.step_price, mn_start_bet)

    elif lot.redemption_price and bet >= lot.redemption_price:
        template = BETS["redemption_bet"]
        args = (None,)
        lot.last_bet = bet
        last_bettor_text = BETS["outbid_redemption"].format(bet)
        to_update_post, to_update_lot = True, True
        update_kwargs["moderation_status"] = LotStatusDB.REDEEMED.value

    elif lot.last_bet and mn_new_bet > bet >= mn_start_bet:
        template = BETS["lt_last"]
        args = (lot.step_price, lot.last_bet)

    else:
        template = BETS["accepted"]
        args = (bet,)
        lot.last_bet = bet
        last_bettor_text = BETS["outbid"].format(bet)
        to_update_post, to_update_lot = True, True

    await w.create_comment(
        owner_id=o.post_owner_id,
        post_id=o.post_id,
        message=template.format(*args),
        reply_to_comment=o.id,
    )
    if to_update_lot:
        await update_lot_data(lot.id, **update_kwargs)
    if to_update_post:
        await edit_post(lot)
    if lot.last_bet_comment and last_bettor_text:
        await w.create_comment(
            owner_id=o.post_owner_id,
            post_id=o.post_id,
            message=last_bettor_text,
            reply_to_comment=lot.last_bet_comment,
        )
