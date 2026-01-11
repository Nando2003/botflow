class PipelineExceptedError(Exception):
    def __init__(self, message: str, popup_message: str | None = None):
        super().__init__(message)
        self.popup_message = popup_message or message
