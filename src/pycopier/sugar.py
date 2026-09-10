from .models import StartRequest, Account
from .client import CopierService

class CopierSugar:
    """High-level convenience API for constructing copiers with fluent syntax."""
    def __init__(self):
        self.req = StartRequest()
        self.endpoint = "copy.mrpc.pro:443"

    @classmethod
    def create(cls):
        return cls()

    def with_credentials(self, user_key: str, manager_key: str = ""):
        self.req.user_key = user_key
        self.req.manager_key = manager_key or user_key
        return self

    def from_master(self, type="MT5", user=0, password="", server="", name=""):
        self.req.master = Account(type=type, user=user, password=password, server=server, name=name)
        return self

    def to_slave(self, type="MT5", user=0, password="", server="", name=""):
        self.req.slave = Account(type=type, user=user, password=password, server=server, name=name)
        return self

    def with_lot_multiplier(self, multiplier: float):
        self.req.risk_type = "LotMultiplier"
        self.req.risk_value = str(multiplier)
        return self

    def with_fixed_lot(self, lot: float):
        self.req.risk_type = "FixedLot"
        self.req.risk_value = str(lot)
        return self

    def copy_sl(self, val: bool = True):
        self.req.copy_sl = val
        return self

    def copy_tp(self, val: bool = True):
        self.req.copy_tp = val
        return self

    async def start(self):
        svc = CopierService(self.endpoint, self.req.user_key, self.req.manager_key)
        res = await svc.start(self.req)
        await svc.close()
        return res
