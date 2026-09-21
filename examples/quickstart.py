import asyncio
import os
import sys

# Ensure local package import works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pycopier import CopierService, DemoAccountClient, Account, StartRequest

async def main():
    print("=== PyCopier Quick Start Demo ===")
    api_key = "TRIAL"
    demo = DemoAccountClient("https://mt5.mrpc.pro")

    # 1. Provision live demo account
    print("\n[1] Provisioning live demo account on MetaQuotes-Demo...")
    master = await demo.open_demo_account(server="MetaQuotes-Demo", api_key=api_key)
    print(f"    Master account created: #{master.login} (Server: {master.server})")

    # 2. Connect terminal via ConnectEx with APIKey: TRIAL
    print(f"\n[2] Connecting terminal via ConnectEx (APIKey: {api_key})...")
    conn = await demo.connect_ex(user=master.login, password=master.password, server=master.server, api_key=api_key)
    print(f"    Terminal Connected! Instance GUID: {conn.terminal_instance_guid}")

    # 3. Verify Trade Copier Gateway
    print("\n[3] Interacting with Copier Service (user_key: TRIAL)...")
    copier = CopierService("copy.mrpc.pro:443", user_key=api_key)
    list_reply = await copier.list()
    print(f"    Active copiers for {api_key}: {len(list_reply.copiers)}")

    # 4. Cleanly Disconnect Terminal Session
    print(f"\n[4] Disconnecting terminal session {conn.terminal_instance_guid}...")
    disc = await demo.disconnect(conn.terminal_instance_guid, api_key=api_key)
    print(f"    Terminal Cleanly Disconnected: {disc.unique_identifier} (Lifetime: {disc.lifetime_seconds}s)")

    await copier.close()
    print("\n=== PyCopier Quick Start Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(main())
