from morne.sdk.app.Event import Event


class ConnectEvent(Event):
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def endpoint(self):
        return self._endpoint

    def __str__(self):
        return "<Connect Event: Endpoint = %s>" % self.endpoint()