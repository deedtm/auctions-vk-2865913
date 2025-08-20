from asyncio import sleep

from vkbottle.exception_factory.base_exceptions import VKAPIError

import captcha_api as captcha

from .config import err_handler, logger


async def vk_api_14_handler(e: VKAPIError):
    logger.warning("Captcha required! Trying to solve...")
    redirect_uri = e.kwargs.get('redirect_uri')
    if not redirect_uri:
        logger.error('Not found redirect_uri in captcha error object! Sleeping for 300 seconds...')
        sleep(300)
        return
    result = await captcha.solve(redirect_uri)
    if result is None:
        return
    solution_token = result.get('solution', {}).get('token')
    with open('captcha_api/solution_tokens.txt', 'a') as f:
        f.write(f'\n{result.get('createTime')}: {solution_token}')
    logger.info(f'Solved captcha: -{result['cost']}₽')


async def vk_api_9_handler(e: VKAPIError):
    try:
        print("[FLOOD CONTROL ERROR]", str(e), sep="\n\n")
        logger.warning("Catched flood control. Sleeping for 120 seconds...")
        await sleep(120)
    except Exception:
        sleep(10)


@err_handler.register_error_handler(VKAPIError)
async def vk_api_handler(e: VKAPIError):
    if e.code == 14:
        await vk_api_14_handler(e)
    elif e.code == 9:
        await vk_api_9_handler
    else:
        logger.error(f"VK API Error {e.code}: {e.error_msg}")
