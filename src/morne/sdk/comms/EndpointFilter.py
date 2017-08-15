class EndpointFilter:
    def __init__(self, endpoint):
        self._endpoint = endpoint

    def endpoint(self):
        return self._endpoint

    def handle_data_from_remote(self, data):
        raise NotImplemented()

    def handle_data_from_app(self, data):
        raise NotImplemented()

    def connected(self):
        pass

    def disconnected(self):
        pass