class CaptchaFailed(BaseException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        kwargs = kwargs


class CaptchaEmptyResponse(BaseException):
    def __init__(self, *args):
        super().__init__(*args)
