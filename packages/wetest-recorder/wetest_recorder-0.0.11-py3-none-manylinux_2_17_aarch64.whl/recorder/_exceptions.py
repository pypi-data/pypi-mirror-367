class RecorderException(Exception):

    def __init__(
        self,
        exception_type: str = "[Recorder Exception]",
        message: str = "Screen Recorder Failed",
    ) -> None:
        self.type = exception_type
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.type} {self.message}"


class DeviceError(RecorderException):
    def __init__(self, message: str) -> None:
        exception_type = "[Device Error]"
        super().__init__(exception_type, message)


class ServerError(RecorderException):
    def __init__(self, message: str) -> None:
        exception_type = "[Scrcpy Server Error]"
        super().__init__(exception_type, message)


class InstanceError(RecorderException):

    def __init__(self, message: str) -> None:
        exception_type = "[Recorder Instance Error]"
        super().__init__(exception_type, message)
