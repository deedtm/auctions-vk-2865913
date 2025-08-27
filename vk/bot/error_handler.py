from asyncio import sleep

from vkbottle.bot import Message
from vkbottle.exception_factory.base_exceptions import VKAPIError

import captcha_api as captcha
from database.lots import Lot
from templates import ERRORS

from .config import err_handler, logger


async def vk_api_14_handler(e: VKAPIError):
    logger.debug("Captcha required! Trying to solve...")
    redirect_uri = e.kwargs.get("redirect_uri")
    if not redirect_uri:
        logger.error(
            "Not found redirect_uri in captcha error object! Sleeping for 300 seconds..."
        )
        sleep(300)
        return
    try:
        result = await captcha.solve(redirect_uri)
        if result is None:
            return
        # solution_token = result.get("solution", {}).get("token")
        logger.info(f'Solved captcha: -{result["cost"]}₽')
    except captcha.errors.CaptchaFailed as err:
        logger.error(f"{err.description}: {err.error_id} {err.code}")


async def vk_api_9_handler(msg: Message):
    sleep_delay = 120
    await msg.answer(ERRORS["flood_control"].format(sleep_delay))
    await sleep(sleep_delay)


async def vk_api_901_handler(lot: Lot):
    logger.debug(f"Failed to send message to user {lot.user_id}")


@err_handler.register_error_handler(VKAPIError)
async def vk_api_handler(e: VKAPIError, *wrapped_args, **wrapped_kwargs):
    if e.code == 14:
        await vk_api_14_handler(e)
    elif e.code == 9:
        await vk_api_9_handler(**wrapped_kwargs)
    elif e.code == 901:
        await vk_api_901_handler()
    else:
        logger.error(f"VK API Error {e.code}: {e.error_msg}")
