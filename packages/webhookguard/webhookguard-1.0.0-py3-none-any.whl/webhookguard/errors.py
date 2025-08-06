class WebhookGuardError(Exception):
    def __init__(self, message, reason):
        super().__init__(message)
        self.reason = reason

    def __str__(self):
        return f'{self.reason}: {super().__str__()}'
