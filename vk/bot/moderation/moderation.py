from vkbottle.bot import Message
from database.lots.models import Lot
from config.vk import fake_moderation_duration, MODERATION_INTERVAL, RESULTS_INTERVAL
from database.lots.utils import (
    is_lot_sended,
    get_pending_lots,
    get_unsended_lots,
    update_lot_data,
)
from ..config import api, MODERATORS_IDS, logger
from ...utils import get_self_group
from asyncio import sleep
from enums.moderation import LotStatusDB, ModerationResult
from templates import MODERATION
from random import randint


async def moderation_wrapper():
    while True:
        try:
            await send_to_moderators()
            await sleep(MODERATION_INTERVAL)
        except Exception as e:
            logger.error(f"moderation_wrapper: {e.__class__.__name__}: {e}")
            return


async def send_to_moderators():
    pending = await get_pending_lots()
    if not pending:
        return

    for id in MODERATORS_IDS:
        await _send_to_moderator(pending, id)


async def _send_to_moderator(pending: list[Lot], user_id: int):
    # send message with keyboard

    ### FAKE MODERATION ###
    await sleep(fake_moderation_duration())
    for lot in pending:
        await _set_result(lot)
    ### ############### ###


# handler of moderator's decision by keyboard
async def _set_result(lot: Lot):
    # result depends on the decision
    result = ModerationResult.APPROVED.value  # or ModerationResult.REJECTED.value

    await update_lot_data(
        lot.id,
        moderation_result=result,
    )

    if await is_lot_sended(lot.id):
        return

    response = "ok"  # == message.text

    await update_lot_data(
        lot.id,
        moderation_status=LotStatusDB.MODERATED.value,
        moderation_result=result,
        moderation_response=response,
    )


async def send_results_wrapper():
    group = await get_self_group(api)
    while True:
        try:
            await send_results(group)
            await sleep(RESULTS_INTERVAL)
        except Exception as e:
            logger.error(f"send_results_wrapper: {e.__class__.__name__}: {e}")
            return


async def send_results(group):
    lots = await get_unsended_lots(group.id)
    for lot in lots:
        await _send_result(lot)


async def _send_result(lot: Lot):
    args = [lot.description]
    if lot.moderation_result == ModerationResult.REJECTED.value:
        args.append(lot.moderation_response or "")
    text = MODERATION[lot.moderation_result].format(*args)
    await api.messages.send(lot.user_id, message=text, random_id=randint(10**6, 10**8))
