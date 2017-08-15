from morne.sdk.app.Event import Event


class DisconnectEvent(Event):
    def __init__(self, endpoint, reason):
        self._endpoint = endpoint
        self._reason = reason

    def endpoint(self):
        return self._endpoint

    def reason(self):
        return self._reason

    def __str__(self):
        return "<Disconnect Event: Endpoint = %s; Reason = %s>" % (self.endpoint(), self._reason)

