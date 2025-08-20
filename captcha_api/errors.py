class CaptchaFailed(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.kwargs = kwargs
        self.error_id = kwargs.get("errorId")
        self.code = kwargs.get("errorCode")
        self.description = kwargs.get(
            "errorDescription", "No description provided"
        )


class CaptchaEmptyResponse(BaseException):
    def __init__(self, *args):
        super().__init__(*args)
