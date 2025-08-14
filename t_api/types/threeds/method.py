import base64
import json
from dataclasses import dataclass

REQUEST_FORMAT = """<body onload="document.form.submit()">
<form name="form" action="{threeds_method_url}" method="post">
  <input type="hidden" name="threeDSMethodData" value="{threeds_method_data}">
</form>
</body>"""


@dataclass
class ThreeDSMethod:
    threeds_method_url: str
    threeds_method_notification_url: str
    threeds_server_trans_id: str

    @property
    def threeds_method_data(self) -> dict:
        return {
            "threeDSMethodNotificationURL": self.threeds_method_notification_url,
            "threeDSServerTransID": self.threeds_server_trans_id,
        }

    @property
    def encoded_threeds_method_data(self) -> str:
        data_json = json.dumps(self.threeds_method_data)
        return base64.b64encode(data_json.encode()).decode()

    def to_html(self) -> str:
        return REQUEST_FORMAT.format(
            threeds_method_url=self.threeds_method_url,
            threeds_method_data=self.encoded_threeds_method_data,
        )


@dataclass
class ThreeDSMethodResponse:
    threeds_server_trans_id: str

    def from_dict(cls, data: dict):
        return cls(threeds_server_trans_id=data.get("threeDSServerTransID", ""))
