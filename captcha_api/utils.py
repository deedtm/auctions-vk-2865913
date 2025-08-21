from asyncio import sleep

import aiohttp
from fake_useragent import UserAgent

from .config import *
from .errors import *
from .log import logger

CREATE_TASK_URL = BASE_URL + "createTask"
GET_TASK_RESULT_URL = BASE_URL + "getTaskResult"


async def post(url: str, json_data: dict, **session_kwargs):
    async with aiohttp.ClientSession(**session_kwargs) as session:
        async with session.post(url, json=json_data) as res:
            return await res.json()


async def create_task(redirect_uri: str):
    ua = UserAgent(os=["Ubuntu"], platforms=["desktop"]).random
    data = {
        "clientKey": RUCAPTCHA_TOKEN,
        "task": {
            "type": "VKCaptchaTask",
            "redirectUri": redirect_uri,
            "userAgent": ua,
            "proxyType": PROXY_TYPE,
            "proxyAddress": PROXY_IP,
            "proxyPort": PROXY_PORT,
            "proxyPassword": PROXY_PASSWORD,
        },
    }
    if PROXY_USERNAME:
        data["task"]["proxyLogin"] = PROXY_USERNAME
    res = await post(CREATE_TASK_URL, data, headers={"User-Agent": ua})
    if res["errorId"] != 0:
        raise CaptchaFailed(**res)
    return res


async def get_task_result(task_id: int):
    data = {"clientKey": RUCAPTCHA_TOKEN, "taskId": task_id}
    res = await post(GET_TASK_RESULT_URL, data)
    return res


async def solve(redirect_uri: str, try_: int = 1):
    if try_ > 100:
        logger.warning("Captcha solving try exceeded 100. Stopping tries")
        return
    create_task_data = await create_task(redirect_uri)
    task_id = create_task_data.get("taskId", -1)

    await sleep(WAITING_RESULT_DELAY)
    result = await get_task_result(task_id)

    i = 1
    while result.get("status") == "processing":
        await sleep(WAITING_RESULT_DELAY)
        result = await get_task_result(task_id)
        logger.info(f"{try_}.{i}. Captcha solving result: {result}")
        i += 1

    if result.get("errorId") == 12:
        logger.info(f"{result['errorDescription']}. Trying again after 10 seconds...")
        await sleep(10)
        return await solve(redirect_uri, try_ + 1)

    if result.get("status") == "ready":
        return result
    elif result.get("errorId") != 0:
        raise CaptchaFailed(**result)
    else:
        raise CaptchaEmptyResponse()
