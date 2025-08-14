from .. import post
from ..config import BASE_URL
from ..types.payments import *

INIT_URL = BASE_URL + "Init"
FINISH_AUTHORIZE_URL = BASE_URL + "FinishAuthorize"
GET_STATE_URL = BASE_URL + "GetState"
CHECK_ORDER_URL = BASE_URL + "CheckOrder"
GET_CONFIRM_OPERATION_URL = BASE_URL + "GetConfirmOperation"


async def init(payment_init: PaymentInit) -> PaymentInitResponse:
    data = await post(INIT_URL, json_data=payment_init.to_dict())
    return PaymentInitResponse.from_dict(PaymentInitResponse, data)


async def finish_authorize(
    finish_authorize_obj: FinishAuthorize,
) -> (
    FinishAuthorizeResponse
    | FinishAuthorizeResponse3DS
    | FinishAuthorizeResponse3DSv2APP
    | FinishAuthorizeResponse3DSv2WEB
):
    data = await post(FINISH_AUTHORIZE_URL, json_data=finish_authorize_obj.to_dict())
    if "MD" in data:
        o = FinishAuthorizeResponse3DS
    elif "AcsSignedContent" in data:
        o = FinishAuthorizeResponse3DSv2APP
    elif "ACSUrl" in data:
        o = FinishAuthorizeResponse3DSv2WEB
    else:
        o = FinishAuthorizeResponse

    return o.from_dict(o, data)


async def get_state(get_state_obj: GetState) -> GetStateResponse:
    data = await post(GET_STATE_URL, json_data=get_state_obj.to_dict())
    return GetStateResponse.from_dict(GetStateResponse, data)


async def check_order(check_order_obj: CheckOrder) -> CheckOrderResponse:
    data = await post(CHECK_ORDER_URL, json_data=check_order_obj.to_dict())
    return CheckOrderResponse.from_dict(CheckOrderResponse, data)


async def get_confirm_operation(
    confirm_operation: GetConfirmOperationURL | GetConfirmOperationEmail,
) -> GetConfirmOperationResponse:
    data = await post(GET_CONFIRM_OPERATION_URL, json_data=confirm_operation.to_dict())
    return GetConfirmOperationResponse.from_dict(GetConfirmOperationResponse, data)


__all__ = (
    "init",
    "finish_authorize",
    "get_state",
    "check_order",
    "get_confirm_operation",
)
