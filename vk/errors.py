class LotNotEnoughDataError(Exception):
    def __init__(self, data):
        self.data = data
        super().__init__("Not enough data provided for lot")
