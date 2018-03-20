class Error:
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return str(self._msg)


class InvalidModeError(Error):
    def __init__(self, msg):
        super().__init__(msg)