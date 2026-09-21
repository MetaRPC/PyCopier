import grpc

class CopierAccount:
    """Low-level gRPC protocol layer for PyCopier."""
    def __init__(self, endpoint: str, user_key: str, manager_key: str = ""):
        self.endpoint = endpoint
        self.user_key = user_key
        self.manager_key = manager_key or user_key
        self.channel = grpc.aio.secure_channel(endpoint, grpc.ssl_channel_credentials())

    def get_metadata(self):
        return (
            ("authorization", f"Bearer {self.user_key}"),
            ("x-metarpc-client-sdk", "PyCopier/1.0.0")
        )

    async def close(self):
        await self.channel.close()
