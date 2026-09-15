# PyCopier — Cloud Trade Copier Python SDK for MetaTrader 4 & 5

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docs](https://img.shields.io/badge/docs-PyCopier-0083ff.svg)](https://github.com/MetaRPC/PyCopier/tree/main/docs)
[![Latency](https://img.shields.io/badge/execution-<20ms-success.svg)](https://mrpc.pro)
[![Cloud](https://img.shields.io/badge/VPS-Not_Required-brightgreen.svg)](https://mrpc.pro)

> **Official Python SDK for MetaRPC Cloud Trade Copier (`copy.mrpc.pro:443`).**  
> Replicate trades in real time across MetaTrader 4 and MetaTrader 5 accounts with sub-20ms execution latency — **without running desktop terminals or Windows VPS.**

---

## ⚡ Why MetaRPC Trade Copier?

- **Cross-Platform & Cross-Broker**: Copy effortlessly from **MT4 to MT5**, **MT5 to MT4**, MT4 to MT4, or MT5 to MT5.
- **Zero Terminal / VPS Requirement**: Entire trade synchronization runs in high-speed cloud memory co-located with London (LD4) and New York (NY4) brokers.
- **Built for Prop Firms & Fund Managers**: Replicate master signals to 100+ slave accounts simultaneously with custom lot sizing, risk rules, and slippage guards.
- **Advanced Risk Controls**:
  - Fixed Lot or Proportional Lot Multiplier
  - Reverse Trading / Inverted Orders
  - Copy Stop Loss (SL) & Take Profit (TP)
  - Max Drawdown and equity stop protections

---

## 📦 Installation

```bash
pip install pycopier
```

---

## 🚀 30-Second Quick Start

```python
import asyncio
from pycopier import CopierService, StartRequest, Account

async def main():
    # 1. Connect to MetaRPC Trade Copier Cloud Service
    # Get your free API key at https://mrpc.pro/signup
    copier = CopierService("copy.mrpc.pro:443", user_key="your_mrpc_api_key")

    # 2. Define Master and Slave MetaTrader accounts
    master_account = Account(
        type="MT5",
        user=10001,
        password="master_password",
        server="MetaQuotes-Demo"
    )

    slave_account = Account(
        type="MT5",
        user=20002,
        password="slave_password",
        server="ICMarkets-Demo"
    )

    # 3. Configure trade replication settings
    request = StartRequest(
        user_key="your_mrpc_api_key",
        master=master_account,
        slave=slave_account,
        risk_type="LotMultiplier",
        risk_value="1.0",           # 1:1 lot ratio
        copy_sl_tp=True             # Mirror Stop Loss & Take Profit
    )

    # 4. Start trade replication
    print("Starting Cloud Trade Copier...")
    response = await copier.start_copier(request)
    print(f"Copier Active! Instance ID: {response.instance_id}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔑 Getting Your API Key & Free Trial

1. **Sign Up**: Create your free account at [https://mrpc.pro/signup](https://mrpc.pro/signup).
2. **Copy API Key**: Open your portal dashboard at [https://mrpc.pro/my](https://mrpc.pro/my) to copy your API token.
3. **Web GUI Management**: You can also monitor and manage copiers via the visual web UI at [https://mrpc.pro/my](https://mrpc.pro/my).

---

## 🌐 Production Endpoints

| Environment | Host / URL | Port | Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Copier Production gRPC** | `copy.mrpc.pro` | `443` | TLS / gRPC | Real-time low-latency copier engine |
| **Web Portal / Copier GUI** | [https://mrpc.pro/my](https://mrpc.pro/my) | `443` | HTTPS | Monitor trade logs, cycles & latency |
| **Account Registration** | [https://mrpc.pro/signup](https://mrpc.pro/signup) | `443` | HTTPS | Instant free trial registration |

---

## 🏢 Compatible Brokers & Prop Firms

Works seamlessly across 500+ MetaTrader server environments:
- **Prop Firms**: FTMO, FundedNext, The Funded Trader, E8 Funding, Alpha Capital, SurgeTrader.
- **Brokers**: IC Markets, Pepperstone, Exness, Tickmill, XM, FXCM, FP Markets, Eightcap, AvaTrade.

---

## 📚 Documentation & Guides

- 📖 [Trade Copier Documentation](https://github.com/MetaRPC/PyCopier/tree/main/docs)
- 🚀 [Quick Start Walkthrough](https://github.com/MetaRPC/PyCopier/blob/main/docs/All_Guides/Your_First_Project.md)
- ⚙️ [Copier Parameters Reference](https://github.com/MetaRPC/PyCopier/blob/main/docs/API_Reference/Copier_Parameters.md)

---

## 📄 License

This SDK is open-sourced under the [MIT License](LICENSE).  
Cloud infrastructure and copier execution engines are operated by [MetaRPC](https://mrpc.pro).
