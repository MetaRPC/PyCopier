import uuid
from typing import AsyncGenerator
import grpc
from .models import StartRequest, StartReply, ListReply, CopierSummary, SimpleReply, TradeLog
from .account import CopierAccount
from .copier_pb2_grpc import CopierServiceStub
from . import copier_pb2 as pb

class CopierService:
    """Wrapper methods layer for MetaRPC Trade Copier via gRPC."""
    def __init__(self, endpoint: str = "copy.mrpc.pro:443", user_key: str = "", manager_key: str = ""):
        self.account = CopierAccount(endpoint, user_key, manager_key)
        self.stub = CopierServiceStub(self.account.channel)

    async def start(self, request: StartRequest) -> StartReply:
        req = pb.StartRequest(
            user_key=request.user_key or self.account.user_key,
            manager_key=request.manager_key or self.account.manager_key,
            master=pb.Account(
                type=request.master.type,
                user=request.master.user,
                password=request.master.password,
                server=request.master.server,
                name=request.master.name,
                id=request.master.id
            ),
            slave=pb.Account(
                type=request.slave.type,
                user=request.slave.user,
                password=request.slave.password,
                server=request.slave.server,
                name=request.slave.name,
                id=request.slave.id
            ),
            risk_type=request.risk_type,
            risk_value=request.risk_value,
            fixed_master_balance=request.fixed_master_balance,
            copy_sl=request.copy_sl,
            copy_tp=request.copy_tp,
            copy_pending_orders=request.copy_pending_orders,
            reverse_copy=request.reverse_copy
        )
        try:
            res = await self.stub.Start(req, metadata=self.account.get_metadata(), timeout=180)
            return StartReply(ok=res.ok, copier_id=res.copier_id, error=res.error)
        except grpc.RpcError as e:
            return StartReply(ok=False, copier_id="", error=e.details() if hasattr(e, "details") else str(e))

    async def list(self) -> ListReply:
        req = pb.ListRequest(user_key=self.account.user_key)
        try:
            res = await self.stub.List(req, metadata=self.account.get_metadata(), timeout=10)
            copiers = [
                CopierSummary(
                    id=c.id,
                    master_type=c.master_type,
                    master_user=c.master_user,
                    master_server=c.master_server,
                    slave_type=c.slave_type,
                    slave_user=c.slave_user,
                    slave_server=c.slave_server,
                    risk_type=c.risk_type,
                    risk_value=c.risk_value,
                    paused=c.paused,
                    pause_reason=c.pause_reason
                )
                for c in res.copiers
            ]
            return ListReply(ok=res.ok, copiers=copiers, error=res.error)
        except grpc.RpcError as e:
            return ListReply(ok=False, copiers=[], error=e.details() if hasattr(e, "details") else str(e))

    async def pause(self, copier_id: str, paused: bool) -> SimpleReply:
        req = pb.PauseRequest(user_key=self.account.user_key, copier_id=copier_id, paused=paused)
        try:
            res = await self.stub.Pause(req, metadata=self.account.get_metadata(), timeout=10)
            return SimpleReply(ok=res.ok, error=res.error)
        except grpc.RpcError as e:
            return SimpleReply(ok=False, error=e.details() if hasattr(e, "details") else str(e))

    async def remove(self, copier_id: str) -> SimpleReply:
        req = pb.RemoveRequest(user_key=self.account.user_key, copier_id=copier_id)
        try:
            res = await self.stub.Remove(req, metadata=self.account.get_metadata(), timeout=10)
            return SimpleReply(ok=res.ok, error=res.error)
        except grpc.RpcError as e:
            return SimpleReply(ok=False, error=e.details() if hasattr(e, "details") else str(e))

    async def stream_trade_logs(self, copier_id: str) -> AsyncGenerator[TradeLog, None]:
        # Only real server messages are yielded. Transport/authentication errors propagate.
        import json
        from urllib.parse import quote
        from websockets.asyncio.client import connect
        uri = f"wss://{self.account.endpoint}/OnTradeLog?id={quote(copier_id, safe='')}"
        async with connect(uri, additional_headers=dict(self.account.get_metadata()),
                           open_timeout=10, max_size=4 * 1024 * 1024) as ws:
            async for message in ws:
                data = json.loads(message)
                if not isinstance(data, dict):
                    raise ValueError("Expected a trade-log object")
                lower = {k.lower(): v for k, v in data.items()}
                master = {k.lower(): v for k, v in (lower.get("masterorder") or {}).items()}
                slave = {k.lower(): v for k, v in (lower.get("slaveorder") or {}).items()}
                yield TradeLog(
                    id=lower.get("id", ""), copier_id=lower.get("copierid", ""),
                    symbol=lower.get("slavesymbol", lower.get("symbol", "")),
                    update_type=str(lower.get("updatetype", "")),
                    master_ticket=int(lower.get("masterticket", master.get("ticket", 0)) or 0),
                    slave_ticket=int(lower.get("slaveticket", slave.get("ticket", 0)) or 0),
                    profit=float(lower.get("profit", slave.get("profit", 0)) or 0),
                    success=lower.get("success", False), raw=data)

    async def close(self):
        await self.account.close()
