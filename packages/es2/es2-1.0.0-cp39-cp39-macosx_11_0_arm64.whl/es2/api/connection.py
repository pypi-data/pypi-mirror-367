import grpc

###################################
# Connection Class
###################################


class Connection:
    def __init__(self, server_address: str):
        self.server_address = server_address
        self.channel = grpc.insecure_channel(server_address)
        try:
            grpc.channel_ready_future(self.channel).result(timeout=3)
            self._connected = True
        except grpc.FutureTimeoutError:
            self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_channel(self):
        return self.channel

    def close(self):
        self.channel.close()
        self._connected = False
