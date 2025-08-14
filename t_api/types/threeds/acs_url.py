import base64
import json
from dataclasses import dataclass
from typing import Optional

__REQUEST_3DSV1 = """<body onload="document.form.submit()" >
<form name="form" action="{acs_url}" method="post" >
  <input type="hidden" name="TermUrl" value="{term_url}" >
  <input type="hidden" name="MD" value="{md}" >
  <input type="hidden" name="PaReq" value="{pa_req}" >
</form>
</body>"""

__REQUEST_3DSV2 = """<body onload="document.form.submit()">
<form name="form" action="{acs_url}" method="post">
  <input type="hidden" name="creq" value="{creq}">
</form>
</body>"""


@dataclass
class ACSUrl3DSv1:
    acs_url: str
    md: str
    pa_req: str
    term_url: str

    def to_html(self) -> str:
        return __REQUEST_3DSV1.format(
            acs_url=self.acs_url, term_url=self.term_url, md=self.md, pa_req=self.pa_req
        )


@dataclass
class ACSUrl3DSv2:
    acs_url: str
    threeds_server_trans_id: str
    acs_trans_id: str
    challenge_window_size: str
    message_type: str
    message_version: str

    @property
    def creq(self) -> dict:
        return {
            "threeDSServerTransID": self.threeds_server_trans_id,
            "acsTransID": self.acs_trans_id,
            "challengeWindowSize": self.challenge_window_size,
            "messageType": self.message_type,
            "messageVersion": self.message_version,
        }

    @property
    def encoded_creq(self) -> str:
        data_json = json.dumps(self.creq)
        return base64.b64encode(data_json.encode()).decode()

    def to_html(self) -> str:
        return __REQUEST_3DSV2.format(acs_url=self.acs_url, creq=self.encoded_creq)


@dataclass(frozen=True)
class ACSUrl3DSv1Response:
    md: str
    pa_res: str
    fallback_on_tds_v1: str

    def from_dict(cls, data: dict):
        return cls(
            md=data.get("MD", ""),
            pa_res=data.get("PaRes", ""),
            fallback_on_tds_v1=data.get("FallbackOnTdsV1", ""),
        )


@dataclass(frozen=True)
class ACSUrl3DSv2Response:
    cres: str

    def from_dict(cls, data: dict):
        return cls(cres=data.get("CRes", ""))
