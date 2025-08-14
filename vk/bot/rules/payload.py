from vkbottle import GroupTypes
from vkbottle.dispatch.rules import ABCRule


class PayloadFilter(ABCRule[GroupTypes.MessageEvent]):
    def __init__(self, payload: dict | list[dict]):
        if isinstance(payload, dict):
            payload = [payload]
        self.payload = payload

    async def check(self, event: GroupTypes.MessageEvent) -> bool:
        pl, self_pl = event.object.payload, self.payload
        res = pl in self_pl

        if isinstance(pl, dict) and not res:
            key = list(pl.keys())[0]
            for sp in self_pl:
                if key not in sp:
                    continue
                sp_value, pl_value = sp[key], pl[key]
                if "{}" in sp_value:
                    bracket_ind = sp_value.find("{}")
                    sp_value = sp_value[:bracket_ind]
                    pl_value = pl_value[:bracket_ind]
                res = res or pl_value == sp_value
                break

        return res
