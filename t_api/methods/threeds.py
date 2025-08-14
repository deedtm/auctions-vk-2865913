from .. import post
from ..config import BASE_URL
from ..types.threeds import *

CHECK_VERSION_URL = BASE_URL + "Check3dsVersion"


async def check_version(
    tds_check_version: ThreeDSCheckVersion,
) -> ThreeDSCheckVersionResponse:
    data = await post(CHECK_VERSION_URL, json_data=tds_check_version.to_dict())
    return ThreeDSCheckVersionResponse.from_dict(ThreeDSCheckVersionResponse, data)


async def method(
    tds_method: ThreeDSMethod,
) -> ThreeDSMethodResponse:
    data = await post(tds_method.threeds_method_url, data=tds_method.to_html())
    return ThreeDSMethodResponse.from_dict(ThreeDSMethodResponse, data)


async def acs_url(
    acs_url_obj: ACSUrl3DSv1 | ACSUrl3DSv2,
) -> ACSUrl3DSv1Response | ACSUrl3DSv2Response:
    data = await post(acs_url_obj.acs_url, json_data=acs_url_obj.to_dict())

    if isinstance(acs_url_obj, ACSUrl3DSv1):
        o = ACSUrl3DSv1Response
    elif isinstance(acs_url_obj, ACSUrl3DSv2):
        o = ACSUrl3DSv2Response

    return o.from_dict(o, data)


__all__ = ("check_version", "method", "acs_url")
