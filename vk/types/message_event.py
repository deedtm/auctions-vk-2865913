from random import randint

from vkbottle import GroupTypes


class MessageEvent(GroupTypes.MessageEvent):
    async def answer(self, text: str, **kwargs):
        await self.ctx_api.messages.send(
            random_id=randint(10**6, 10**9),
            peer_id=self.object.peer_id,
            message=text,
            **kwargs
        )

    async def edit_message(self, text: str, **kwargs):
        await self.ctx_api.messages.edit(
            peer_id=self.object.peer_id,
            message=text,
            cmid=self.object.conversation_message_id,
            **kwargs
        )

    async def delete(self):
        await self.ctx_api.messages.delete(
            peer_id=self.object.peer_id,
            cmids=[self.object.conversation_message_id],
            delete_for_all=True,
        )
