import json

import aiohttp


async def get(url: str, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, **kwargs) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 400:
                error_data = await response.json()
                raise Exception(f"Bad request: {json.dumps(error_data, indent=2)}")
            else:
                raise Exception(f"Failed to get data: {response.status}")


async def post(url: str, json_data: dict = None, data: dict = None, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_data, data=data, **kwargs) as response:
            if response.status == 200:
                return await response.json()
            else:
                try:
                    error_data = await response.json()
                    raise Exception(f"Error occurred: {json.dumps(error_data, indent=2)}")
                except:
                    raise Exception(f"Failed to post data: {response.status} {response.reason}")
