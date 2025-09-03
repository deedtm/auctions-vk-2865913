from asyncio import sleep

from vkbottle.bot import Message
from vkbottle.exception_factory.base_exceptions import VKAPIError

import captcha_api as captcha
from database.lots.models import Lot
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


async def vk_api_9_handler(**kwargs):
    sleep_delay = 120
    msg = kwargs.get('msg', kwargs.get('message'))
    if msg:
        await msg.answer(ERRORS["flood_control"].format(sleep_delay))
    else:
        logger.warning(f'No message found in kwargs for vk api 9 error. Given kwargs: {kwargs}')
    await sleep(sleep_delay)


async def vk_api_901_handler(**kwargs):
    user_id = None
    if 'lot' in kwargs:
        user_id = kwargs['lot'].user_id
    if user_id:
        logger.debug(f"Failed to send message to user {user_id}")
    else:
        logger.debug(f"Failed to send message to user (user_id not found, kwargs: {kwargs})")


@err_handler.register_error_handler(VKAPIError)
async def vk_api_handler(e: VKAPIError, *wrapped_args, **wrapped_kwargs):
    if e.code == 14:
        await vk_api_14_handler(e)
    elif e.code == 9:
        await vk_api_9_handler(**wrapped_kwargs)
    elif e.code == 901:
        await vk_api_901_handler(**wrapped_kwargs)
    else:
        logger.error(f"VK API Error {e.code}: {e.error_msg}")
