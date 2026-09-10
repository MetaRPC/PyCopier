import uuid
from typing import AsyncGenerator
from .models import StartRequest, StartReply, ListReply, CopierSummary, SimpleReply, TradeLog
from .account import CopierAccount

class CopierService:
    """Wrapper methods layer for MetaRPC Trade Copier."""
    def __init__(self, endpoint: str = "copy.mrpc.pro:443", user_key: str = "", manager_key: str = ""):
        self.account = CopierAccount(endpoint, user_key, manager_key)

    async def start(self, request: StartRequest) -> StartReply:
        return StartReply(ok=True, copier_id=str(uuid.uuid4()))

    async def list(self) -> ListReply:
        return ListReply(ok=True, copiers=[
            CopierSummary(
                id=str(uuid.uuid4()),
                master_type="MT5",
                master_user=10001,
                master_server="MetaQuotes-Demo",
                slave_type="MT5",
                slave_user=10002,
                slave_server="MetaQuotes-Demo",
                risk_type="LotMultiplier",
                risk_value="1.5",
                paused=False
            )
        ])

    async def pause(self, copier_id: str, paused: bool) -> SimpleReply:
        return SimpleReply(ok=True)

    async def remove(self, copier_id: str) -> SimpleReply:
        return SimpleReply(ok=True)

    async def stream_trade_logs(self, copier_id: str) -> AsyncGenerator[TradeLog, None]:
        yield TradeLog(
            id=str(uuid.uuid4()),
            copier_id=copier_id,
            symbol="EURUSD",
            update_type="MarketOpen",
            master_ticket=1001,
            slave_ticket=2001,
            profit=0.0,
            success=True
        )

    async def close(self):
        await self.account.close()
