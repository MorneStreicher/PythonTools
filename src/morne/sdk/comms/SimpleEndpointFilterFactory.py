import EndpointFilterFactory


class SimpleEndpointFilterFactory(EndpointFilterFactory.EndpointFilterFactory):
    def __init__(self, endpoint_filter_class):
        EndpointFilterFactory.EndpointFilterFactory.__init__(self)
        self._endpoint_filter_class = endpoint_filter_class

    def new_endpoint_filter(self, endpoint_instance):
        return self._endpoint_filter_class(endpoint_instance)
