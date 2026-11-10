import grpc

class CopierAccount:
    """Low-level gRPC protocol layer for PyCopier."""
    def __init__(self, endpoint: str, user_key: str, manager_key: str = ""):
        if not user_key or user_key.upper() == "TRIAL" or any(ord(c) < 33 or ord(c) > 126 for c in user_key):
            raise ValueError("A real owner API key is required (printable ASCII, no whitespace).")
        clean = endpoint.replace("https://", "").replace("http://", "").rstrip("/")
        if ":" not in clean:
            clean = f"{clean}:443"
        self.endpoint = clean
        self.user_key = user_key
        self.manager_key = manager_key or user_key
        self.channel = grpc.aio.secure_channel(clean, grpc.ssl_channel_credentials())

    def get_metadata(self):
        return (
            ("apikey", self.user_key),
            ("x-metarpc-client-sdk", "PyCopier/1.0.0")
        )

    async def close(self):
        await self.channel.close()
