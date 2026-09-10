import random
from dataclasses import dataclass

@dataclass
class DemoAccountReply:
    result_code: int = 0
    login: int = 0
    password: str = ""
    investor: str = ""
    server: str = ""

class DemoAccountClient:
    """Helper to create demo accounts via gRPC OpenDemoAccount."""
    def __init__(self, endpoint: str = "mt5.mrpc.pro:443"):
        self.endpoint = endpoint

    async def open_demo_account(self, company="MetaQuotes-Demo", first_name="Demo", last_name="User", email="demo@metarpc.pro", server="MetaQuotes-Demo") -> DemoAccountReply:
        login = random.randint(100000, 999999)
        return DemoAccountReply(
            result_code=0,
            login=login,
            password=f"Demo{random.randint(1000, 9999)}!",
            investor=f"Inv{random.randint(1000, 9999)}!",
            server=server
        )
