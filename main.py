from vk import bot
from log import get_logger
from logging import INFO
from database.utils import init_schemas


# async def main():
#     bot.loop_wrapper.add_task(init_schemas(), bot.run_polling())
#     bot.loop_wrapper.run()


if __name__ == "__main__":
    logger = get_logger(__name__, INFO)
    logger.info("Starting bot...")
    bot.loop_wrapper.add_task(init_schemas())
    bot.loop_wrapper.add_task(bot.run_polling())
    bot.loop_wrapper.run()