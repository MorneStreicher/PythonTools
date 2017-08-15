from morne.sdk.comms.EndpointFilter import EndpointFilter
from morne.sdk.app.Timer import Timer
from morne.sdk.app.Log import Log
import struct


class EndpointFilterNByteHeader(EndpointFilter):
    def __init__(self, endpoint, n):
        EndpointFilter.__init__(self, endpoint)
        self.buffer = ""
        self.timer = None

        self.n = n
        self.formatter = None
        if n == 2: self.formatter = "!h"
        if n == 4: self.formatter = "!I"
        if not self.formatter:
            raise Exception("Invalid n value!")

    def handle_data_from_app(self, data):
        l = struct.pack(self.formatter,len(data))
        data_to_send = l + data
        self.endpoint().send_data_to_remote(data_to_send)

    def handle_data_from_remote(self, data):
        if self.timer:
            self.timer.stop()
            self.timer = None

        self.buffer += data
        while len(self.buffer) > self.n:
            size_str = self.buffer[0:self.n]
            size = struct.unpack(self.formatter,size_str)[0]
            if len(self.buffer) >= size + self.n:
                data = self.buffer[self.n:size+self.n]
                self.buffer = self.buffer[size+self.n:]
                self.endpoint().send_data_to_app(data)
            else:
                # We don't have enough data to consume yet. Wait for the next packet. But start a 10s timeout timer
                self.timer = Timer.create_callback(None, 10000, self._receive_timeout)
                return

    def _receive_timeout(self):
        Log.log().critical("Terminating / Closing endpoint! Receive timeout on Endpoint [%s], Buffer data = [%s]" %
                           (str(self.endpoint()), self.buffer))
        self.endpoint().close()


class EndpointFilter2ByteHeader(EndpointFilterNByteHeader):
    def __init__(self, endpoint):
        EndpointFilterNByteHeader.__init__(self, endpoint, 2)


class EndpointFilter4ByteHeader(EndpointFilterNByteHeader):
    def __init__(self, endpoint):
        EndpointFilterNByteHeader.__init__(self, endpoint, 4)

