import asyncio
from logging import DEBUG, INFO

from dotenv import load_dotenv
from vkbottle.bot import run_multibot
from vkbottle.tools import LoopWrapper

from config.vk import LOOPING_INITIAL_DELAY
from database.utils import init_schemas
from log import get_logger
from vk.bot import api as bot_api
from vk.bot import bot as bot_bot
from vk.bot.moderation.moderation import moderation_wrapper, send_results_wrapper
from vk.bot.notificator import ban_wrapper, collector_wrapper, loyal_wrapper
from vk.publisher import apis as publisher_apis
from vk.publisher.digest.posting import digest_wrapper
from vk.publisher.end import end_wrapper
from vk.publisher.publish import post_wrapper, reset_posts_amounts_wrapper
from vk.publisher.utils import init_groups


async def the_looping(logger):
    await asyncio.sleep(LOOPING_INITIAL_DELAY)
    try:
        tasks = [
            moderation_wrapper(),
            send_results_wrapper(),
            post_wrapper(),
            reset_posts_amounts_wrapper(),
            end_wrapper(),
            collector_wrapper(),
            ban_wrapper(),
            loyal_wrapper(),
            digest_wrapper(),
        ]
        exceptions = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        for ind, exc in enumerate(exceptions[:-1]):
            if exc is None:
                continue
            logger.error(
                f"Error in {tasks[ind].__name__}: {exc.__class__.__name__} {exc}"
            )
        exceptions = list(filter(lambda x: isinstance(x, Exception), exceptions))
        if exceptions:
            exit(1)
    except KeyboardInterrupt:
        logger.info("Stopping the_looping...")
        return


if __name__ == "__main__":
    load_dotenv()
    logger = get_logger(__name__, DEBUG)
    logger.info("Starting bot...")

    lw = LoopWrapper(
        on_startup=[init_schemas(), init_groups()], tasks=[the_looping(logger)]
    )

    bot_bot.loop_wrapper = lw
    run_multibot(bot_bot, [bot_api] + publisher_apis)
