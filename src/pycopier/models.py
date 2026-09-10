from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Account:
    type: str = "MT5"
    user: int = 0
    password: str = ""
    server: str = ""
    name: str = ""

@dataclass
class StartRequest:
    user_key: str = ""
    manager_key: str = ""
    master: Account = field(default_factory=Account)
    slave: Account = field(default_factory=Account)
    risk_type: str = "LotMultiplier"
    risk_value: str = "1.0"
    fixed_master_balance: str = ""
    copy_sl: bool = True
    copy_tp: bool = True
    copy_pending_orders: bool = False
    reverse_copy: bool = False

@dataclass
class StartReply:
    ok: bool = True
    copier_id: str = ""
    error: str = ""

@dataclass
class CopierSummary:
    id: str = ""
    master_type: str = ""
    master_user: int = 0
    master_server: str = ""
    slave_type: str = ""
    slave_user: int = 0
    slave_server: str = ""
    risk_type: str = ""
    risk_value: str = ""
    paused: bool = False
    pause_reason: str = ""

@dataclass
class ListReply:
    ok: bool = True
    copiers: List[CopierSummary] = field(default_factory=list)
    error: str = ""

@dataclass
class SimpleReply:
    ok: bool = True
    error: str = ""

@dataclass
class TradeLog:
    id: str = ""
    copier_id: str = ""
    symbol: str = ""
    update_type: str = ""
    master_ticket: int = 0
    slave_ticket: int = 0
    profit: float = 0.0
    success: bool = True
