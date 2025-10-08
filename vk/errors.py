class LotNotEnoughDataError(Exception):
    def __init__(self, data):
        self.data = data
        super().__init__("Not enough data provided for lot")


class SavingPhotoError(Exception):
    def __init__(self, attachment, exception):
        self.attachment = attachment
        self.saving_exception = exception
        super().__init__(
            f"Failed to save photos from attachment. Got exception: {exception}"
        )
