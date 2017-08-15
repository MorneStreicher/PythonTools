from morne.sdk.app.Event import Event


class DataEvent(Event):
    def __init__(self, endpoint, data):
        self._endpoint = endpoint
        self._data = data

    def endpoint(self):
        return self._endpoint

    def data(self):
        return self._data

    def __str__(self):
        return "<DataEvent: %s; endpoint = %s>" % (self._data, self._endpoint)