from asyncio import sleep

from fake_useragent import UserAgent
from vkbottle import API

from .config import *
from .errors import *

CREATE_TASK_URL = BASE_URL + "createTask"
GET_TASK_RESULT_URL = BASE_URL + "getTaskResult"


async def create_task(redirect_uri: str, api: API):
    data = {
        "clientKey": RUCAPTCHA_TOKEN,
        "task": {
            "type": "VKCaptchaTask",
            "redirectUri": redirect_uri,
            "userAgent": UserAgent(os=["Ubuntu"], platforms=["desktop"]).random,
            "proxyType": "socks5",
            "proxyAddress": PROXY_IP,
            "proxyPort": PROXY_PORT,
            "proxyPassword": PROXY_PASSWORD,
        },
    }
    return await api.http_client.request_json(CREATE_TASK_URL, "POST", data)


async def get_task_result(api: API, task_id: int):
    data = {"clientKey": RUCAPTCHA_TOKEN, "taskId": task_id}
    return await api.http_client.request_json(GET_TASK_RESULT_URL, "POST", data)


async def solve(api: API, redirect_uri: str):
    task_id = await create_task(redirect_uri, api)

    await sleep(5)
    result = await get_task_result(api, task_id)

    while result.get("status") == "processing":
        await sleep(5)
        result = await get_task_result(api, task_id)

    if result.get("status") == "ready":
        return result
    elif result.get("errorId") != 0:
        raise CaptchaFailed(**result)
    else:
        raise CaptchaEmptyResponse()
