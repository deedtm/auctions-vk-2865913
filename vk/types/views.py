from typing import List, Optional, TypeVar

from vkbottle.dispatch.middlewares import BaseMiddleware
from vkbottle.dispatch.views.bot import BotMessageView, RawBotEventView
from vkbottle.modules import logger

T_contra = TypeVar("T_contra", list, dict, contravariant=True)


class MessageView(BotMessageView):
    async def pre_middleware(
        self,
        event: T_contra,
        context_variables: Optional[dict] = None,
    ) -> Optional[List[BaseMiddleware]]:
        """Run all of the pre middleware methods and return an exception if any error occurs"""
        mw_instances = []

        for middleware in self.middlewares:
            mw_instance = middleware(event, view=self)
            await mw_instance.pre()
            if not mw_instance.can_forward:
                if "doubling" not in str(mw_instance.error).lower():
                    logger.error(
                        "{} pre returned error {}", mw_instance, mw_instance.error
                    )
                return None

            mw_instances.append(mw_instance)

            if context_variables is not None:
                context_variables.update(mw_instance.context_update)

        return mw_instances


class RawEventView(RawBotEventView):
    async def pre_middleware(
        self,
        event: T_contra,
        context_variables: Optional[dict] = None,
    ) -> Optional[List[BaseMiddleware]]:
        """Run all of the pre middleware methods and return an exception if any error occurs"""
        mw_instances = []

        for middleware in self.middlewares:
            mw_instance = middleware(event, view=self)
            await mw_instance.pre()
            if not mw_instance.can_forward:
                if "doubling" not in str(mw_instance.error).lower():
                    logger.error(
                        "{} pre returned error {}", mw_instance, mw_instance.error
                    )
                return None

            mw_instances.append(mw_instance)

            if context_variables is not None:
                context_variables.update(mw_instance.context_update)

        return mw_instances
