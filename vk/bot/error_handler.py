import os
from asyncio import sleep
from random import randint

from vkbottle.exception_factory.base_exceptions import VKAPIError

from .config import api, err_handler, logger


@err_handler.register_error_handler(VKAPIError)
async def vk_api_handler(e: VKAPIError):
    if e.code == 14:
        logger.warning("Captcha required! Using API to notify admins...")
        peer_ids = list(map(int, os.getenv("ADMINS_IDS", "").split()))
        redirect_uri = e.kwargs.get("redirect_uri")
        for pid in peer_ids:
            try:
                await api.messages.send(
                    peer_id=pid,
                    random_id=randint(10**6, 10**7),
                    message=f"[КАПЧА]\n\n{redirect_uri}\n\n❗️  Обязательно обновите страницу после решения капчи",
                )
            except Exception as exc:
                logger.error(
                    f"Failed to notify id{pid} - {exc.__class__.__name__}: {exc}\nCAPTCHA URI: {redirect_uri}"
                )
            await sleep(3)
    else:
        logger.error(f"VK API Error {e.code}: {e.error_msg}")
