from typing import Any, List, Optional, TypeVar

from vkbottle.api import ABCAPI
from vkbottle.dispatch.dispenser.abc import ABCStateDispenser
from vkbottle.dispatch.middlewares import BaseMiddleware
from vkbottle.dispatch.views.bot import BotMessageView, RawBotEventView
from vkbottle.modules import logger
from ..bot.config import err_handler

T_contra = TypeVar("T_contra", list, dict, contravariant=True)
Event_contra = TypeVar("Event_contra", list, dict, contravariant=True)


class MessageView(BotMessageView):
    @err_handler.catch
    async def handle_event(
        self, event: T_contra, ctx_api: "ABCAPI", state_dispenser: "ABCStateDispenser"
    ) -> None:
        logger.debug(
            "Handling event ({}) with message view", self.get_event_type(event)
        )
        context_variables: dict = {}
        message = await self.get_message(event, ctx_api, self.replace_mention)
        message.state_peer = await state_dispenser.cast(self.get_state_key(message))

        for text_ax in self.default_text_approximators:
            message.text = text_ax(message)

        mw_instances = await self.pre_middleware(message, context_variables)
        if mw_instances is None:
            logger.debug("Handling stopped, pre_middleware returned error")
            return

        handle_responses = []
        handlers = []

        for handler in self.handlers:
            result = await handler.filter(message)
            logger.debug("Handler {} returned {}", handler, result)

            if result is False:
                continue

            elif isinstance(result, dict):
                context_variables.update(result)

            handler_response = await handler.handle(message, **context_variables)
            handle_responses.append(handler_response)
            handlers.append(handler)

            return_handler = self.handler_return_manager.get_handler(handler_response)
            if return_handler is not None:
                await return_handler(
                    self.handler_return_manager,
                    handler_response,
                    message,
                    context_variables,
                )

            if handler.blocking:
                break

        await self.post_middleware(mw_instances, handle_responses, handlers)

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
    @err_handler.catch
    async def handle_event(
        self,
        event: Event_contra,
        ctx_api: "ABCAPI",
        state_dispenser: "ABCStateDispenser",
    ) -> Any:
        logger.debug(
            "Handling event ({}) with message view", self.get_event_type(event)
        )

        context_variables: dict = {}
        handle_responses = []
        handlers = []

        mw_instances = await self.pre_middleware(event, context_variables)
        if mw_instances is None:
            logger.info("Handling stopped, pre_middleware returned error")
            return

        for handler_basement in self.get_handler_basements(event):
            event_model = self.get_event_model(handler_basement, event)

            if isinstance(event_model, dict):
                event_model["ctx_api"] = ctx_api
            else:
                event_model.unprepared_ctx_api = ctx_api  # type: ignore

            result = await handler_basement.handler.filter(event_model)
            logger.debug("Handler {} returned {}", handler_basement.handler, result)

            if result is False:
                continue

            elif isinstance(result, dict):
                context_variables.update(result)

            handler_response = await handler_basement.handler.handle(
                event_model, **context_variables
            )
            handle_responses.append(handler_response)
            handlers.append(handler_basement.handler)

            return_handler = self.handler_return_manager.get_handler(handler_response)
            if return_handler is not None:
                await return_handler(
                    self.handler_return_manager,
                    handler_response,
                    event_model,
                    context_variables,
                )

            if handler_basement.handler.blocking:
                break

        await self.post_middleware(mw_instances, handle_responses, handlers)

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
