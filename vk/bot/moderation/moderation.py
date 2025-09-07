from asyncio import sleep
from random import randint

from config.vk import MODERATION_INTERVAL, RESULTS_INTERVAL, fake_moderation_duration
from database.lots.models import Lot
from database.lots.utils import (
    get_pending_lots,
    get_unsended_lots,
    get_lots_by_fields,
    update_lot_data,
)
from enums.moderation import LotStatusDB, ModerationResult
from templates import MODERATION

from ...publisher.utils import get_api
from ..config import MODERATORS_IDS, err_handler, logger


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
    ### REMOVE ALL NEXT LINES WHEN ADDING MODERATION ###
    await sleep(fake_moderation_duration())
    
    for lot in pending:
        db_lot = await get_lots_by_fields(id=lot.id)
        if db_lot and db_lot[0].moderation_status != LotStatusDB.PENDING.value:
            return
        await _set_result(lot)
    #######################


# handler of moderator's decision by keyboard
async def _set_result(lot: Lot):
    # result depends on the decision
    result = ModerationResult.APPROVED.value  # or ModerationResult.REJECTED.value
  
    # await update_lot_data(
    #     lot.id,
    #     moderation_result=result,
    # )

    response = "ok"  # == message.text

    await update_lot_data(
        lot.id,
        moderation_status=LotStatusDB.MODERATED.value,
        moderation_result=result,
        moderation_response=response,
    )


async def send_results_wrapper():
    while True:
        try:
            await send_results()
            await sleep(RESULTS_INTERVAL)
        except Exception as e:
            logger.error(f"send_results_wrapper: {e.__class__.__name__}: {e}")
            return


async def send_results():
    lots = await get_unsended_lots()
    for lot in lots:
        await _send_result(lot)
        await sleep(1)


@err_handler.catch
async def _send_result(lot: Lot):
    args = [lot.description]
    if lot.moderation_result == ModerationResult.REJECTED.value:
        args.append(lot.moderation_response or "")
    text = MODERATION[lot.moderation_result].format(*args)
    api = get_api(lot.group_id)
    await api.messages.send(lot.user_id, message=text, random_id=randint(10**6, 10**8))
