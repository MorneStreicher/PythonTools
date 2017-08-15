import EndpointFilter


class EndpointFilterNull(EndpointFilter.EndpointFilter):
    def __init__(self, endpoint):
        EndpointFilter.EndpointFilter.__init__(self, endpoint)

    def handle_data_from_remote(self, data):
        self.endpoint().send_data_to_app(data)

    def handle_data_from_app(self, data):
        self.endpoint().send_data_to_remote(data)