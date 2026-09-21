import urllib.request
import urllib.parse
import json
import asyncio
from dataclasses import dataclass

@dataclass
class DemoAccountReply:
    result_code: int = 0
    login: int = 0
    password: str = ""
    investor: str = ""
    server: str = ""

@dataclass
class ConnectExReply:
    terminal_instance_guid: str = ""
    terminal_type: str = "MT5"

@dataclass
class DisconnectReply:
    unique_identifier: str = ""
    lifetime_seconds: int = 0

class DemoAccountClient:
    """Production helper for MetaTrader demo account provisioning and terminal lifecycle."""
    def __init__(self, endpoint: str = "https://mt5.mrpc.pro"):
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        self.endpoint = endpoint.rstrip("/")

    async def open_demo_account(self, server: str = "MetaQuotes-Demo", api_key: str = "TRIAL") -> DemoAccountReply:
        def _call():
            url = f"{self.endpoint}/DemoAccount/Open?server={urllib.parse.quote(server)}"
            req = urllib.request.Request(url, headers={"APIKey": api_key, "User-Agent": "PyCopier/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return DemoAccountReply(
                    result_code=data.get("resultCode", 0),
                    login=int(data.get("login", 0)),
                    password=data.get("password", ""),
                    investor=data.get("investor", ""),
                    server=data.get("server", server)
                )
        return await asyncio.to_thread(_call)

    async def connect_ex(self, user: int, password: str, server: str = "MetaQuotes-Demo", api_key: str = "TRIAL") -> ConnectExReply:
        def _call():
            params = urllib.parse.urlencode({"user": user, "password": password, "mtClusterName": server})
            url = f"{self.endpoint}/ConnectEx?{params}"
            req = urllib.request.Request(url, headers={"APIKey": api_key, "User-Agent": "PyCopier/1.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
                term_id = data.get("data", {}).get("terminalInstanceGuid", "")
                return ConnectExReply(terminal_instance_guid=term_id, terminal_type="MT5")
        return await asyncio.to_thread(_call)

    async def disconnect(self, terminal_id: str, api_key: str = "TRIAL") -> DisconnectReply:
        def _call():
            url = f"{self.endpoint}/Disconnect"
            req = urllib.request.Request(url, headers={"APIKey": api_key, "id": terminal_id, "User-Agent": "PyCopier/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                disc = data.get("data", {})
                return DisconnectReply(
                    unique_identifier=disc.get("uniqueIdentifier", ""),
                    lifetime_seconds=disc.get("fullLifeTimeSeconds", 0)
                )
        return await asyncio.to_thread(_call)

    async def order_send(self, terminal_id: str, symbol: str = "EURUSD", operation: str = "TMT5_ORDER_TYPE_BUY", volume: float = 0.01, api_key: str = "TRIAL") -> int:
        def _call():
            params = urllib.parse.urlencode({
                "id": terminal_id,
                "symbol": symbol,
                "operation": operation,
                "volume": f"{volume:.2f}",
                "stoploss": 0,
                "takeprofit": 0,
                "comment": "PyCopier_Test"
            })
            url = f"{self.endpoint}/OrderSend?{params}"
            req = urllib.request.Request(url, headers={"APIKey": api_key, "id": terminal_id, "User-Agent": "PyCopier/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                if isinstance(data, dict):
                    inner = data.get("data", {})
                    if isinstance(inner, dict):
                        return int(inner.get("order") or inner.get("ticket") or 0)
                    return int(data.get("order") or data.get("ticket") or 0)
                return int(data)
        return await asyncio.to_thread(_call)

    async def opened_orders(self, terminal_id: str, api_key: str = "TRIAL") -> list:
        def _call():
            url = f"{self.endpoint}/OpenedOrders?id={terminal_id}"
            req = urllib.request.Request(url, headers={"APIKey": api_key, "id": terminal_id, "User-Agent": "PyCopier/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    inner = data.get("data", {})
                    if isinstance(inner, dict):
                        return inner.get("positionInfos", []) or inner.get("positions", []) or []
                    elif isinstance(inner, list):
                        return inner
                    return data.get("positionInfos", []) or []
                return []
        return await asyncio.to_thread(_call)

    async def order_close(self, terminal_id: str, ticket: int, api_key: str = "TRIAL") -> str:
        def _call():
            params = urllib.parse.urlencode({
                "id": terminal_id,
                "ticket": ticket,
                "volume": 0,
                "slippage": 20
            })
            url = f"{self.endpoint}/OrderClose?{params}"
            req = urllib.request.Request(url, headers={"APIKey": api_key, "id": terminal_id, "User-Agent": "PyCopier/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode()
        return await asyncio.to_thread(_call)

def to_hyphen_guid(guid: str) -> str:
    clean = guid.replace("mt5_live_", "").replace("-", "")
    if len(clean) == 32:
        return f"{clean[0:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:32]}"
    return guid

