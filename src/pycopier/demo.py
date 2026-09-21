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
