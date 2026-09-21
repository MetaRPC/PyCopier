import asyncio
import os
import sys

# Ensure local package import works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pycopier import CopierService, DemoAccountClient, Account, StartRequest
from pycopier.demo import to_hyphen_guid

async def main():
    print("=== MetaRPC PyCopier Trade Replication Quick Start ===")
    api_key = "TRIAL"
    demo = DemoAccountClient("https://mt5.mrpc.pro")
    copier = CopierService("copy.mrpc.pro:443", user_key=api_key)

    master_guid = ""
    slave_guid = ""
    copier_id = ""

    try:
        # 1. Provision live demo accounts
        print("\n[1] Provisioning live demo accounts on MetaQuotes-Demo...")
        master = await demo.open_demo_account(server="MetaQuotes-Demo", api_key=api_key)
        print(f"    Master Account Provisioned: #{master.login} on {master.server}")
        await asyncio.sleep(1)

        slave = await demo.open_demo_account(server="MetaQuotes-Demo", api_key=api_key)
        print(f"    Slave Account Provisioned:  #{slave.login} on {slave.server}")
        await asyncio.sleep(1)

        # 2. Connect terminals via ConnectEx
        print(f"\n[2] Connecting terminals via ConnectEx (APIKey: {api_key})...")
        for attempt in range(1, 4):
            try:
                conn_m = await demo.connect_ex(user=master.login, password=master.password, server=master.server, api_key=api_key)
                if conn_m.terminal_instance_guid:
                    master_guid = conn_m.terminal_instance_guid
                    break
            except Exception as e:
                print(f"    Master ConnectEx attempt {attempt} error: {e}")
            print(f"    Retrying master with fresh demo account...")
            master = await demo.open_demo_account(server="MetaQuotes-Demo", api_key=api_key)
            await asyncio.sleep(2)

        if not master_guid:
            print("    Failed to connect master terminal.")
            return
        print(f"    Master Terminal Connected! GUID: {master_guid}")

        for attempt in range(1, 4):
            try:
                conn_s = await demo.connect_ex(user=slave.login, password=slave.password, server=slave.server, api_key=api_key)
                if conn_s.terminal_instance_guid:
                    slave_guid = conn_s.terminal_instance_guid
                    break
            except Exception as e:
                print(f"    Slave ConnectEx attempt {attempt} error: {e}")
            print(f"    Retrying slave with fresh demo account...")
            slave = await demo.open_demo_account(server="MetaQuotes-Demo", api_key=api_key)
            await asyncio.sleep(2)

        if not slave_guid:
            print("    Failed to connect slave terminal.")
            return
        print(f"    Slave Terminal Connected!  GUID: {slave_guid}")

        master_session_id = to_hyphen_guid(master_guid)
        slave_session_id = to_hyphen_guid(slave_guid)

        # 3. Start Trade Copier via gRPC on copy.mrpc.pro:443
        print("\n[3] Starting Trade Copier via gRPC on copy.mrpc.pro:443...")
        start_req = StartRequest(
            user_key=api_key,
            risk_type="LotMultiplier",
            risk_value="1.0",
            master=Account(
                type="MT5",
                user=master.login,
                password=master.password,
                server=master.server,
                id=master_session_id
            ),
            slave=Account(
                type="MT5",
                user=slave.login,
                password=slave.password,
                server=slave.server,
                id=slave_session_id
            )
        )

        start_rep = await copier.start(start_req)
        print(f"    gRPC Start Reply: ok={start_rep.ok}, copierId={start_rep.copier_id}, error={start_rep.error}")
        if not start_rep.ok:
            print(f"    Copier Start returned error: {start_rep.error}")
            return
        copier_id = start_rep.copier_id

        await asyncio.sleep(4)

        # 4. Place Market Order on Master
        print("\n[4] Opening Market Order on Master (0.01 EURUSD BUY)...")
        master_ticket = await demo.order_send(master_guid, symbol="EURUSD", operation="TMT5_ORDER_TYPE_BUY", volume=0.01, api_key=api_key)
        print(f"    Master Order Placed! Ticket: {master_ticket}")

        # 5. Verify Trade Copied to Slave
        print("\n[5] Verifying replicated trade on Slave account...")
        replicated = False
        for attempt in range(1, 16):
            await asyncio.sleep(2)
            positions = await demo.opened_orders(slave_guid, api_key=api_key)
            print(f"    Attempt {attempt}: Slave active positions count = {len(positions)}")
            if positions:
                first = positions[0]
                ticket = first.get("ticket") or first.get("Ticket")
                symbol = first.get("symbol") or first.get("Symbol")
                volume = first.get("volume") or first.get("Volume")
                op_type = first.get("type") or first.get("Type")
                print(f"    --> CONFIRMED ON SLAVE: Ticket={ticket}, Symbol={symbol}, Volume={volume}, Type={op_type}")
                replicated = True
                break

        if not replicated:
            print("    WARNING: Slave trade replication timed out.")
        else:
            print("    SUCCESS: Trade successfully replicated to slave account!")

        # 6. Close Position on Master
        if master_ticket:
            print(f"\n[6] Closing Master trade ticket #{master_ticket}...")
            close_resp = await demo.order_close(master_guid, master_ticket, api_key=api_key)
            print(f"    Master OrderClose result: {close_resp}")

            # 7. Verify Trade Closed on Slave
            print("\n[7] Verifying trade closed on Slave...")
            for attempt in range(1, 16):
                await asyncio.sleep(2)
                positions = await demo.opened_orders(slave_guid, api_key=api_key)
                if not positions:
                    print("    SUCCESS: Slave position closed by trade copier!")
                    break
                print(f"    Attempt {attempt}: Slave positions still open: {len(positions)}")

        # 8. Remove Copier via gRPC
        if copier_id:
            print(f"\n[8] Removing Copier {copier_id} via gRPC...")
            rem_rep = await copier.remove(copier_id)
            print(f"    Copier Remove Reply: ok={rem_rep.ok}")

    finally:
        # 9. Cleanly Disconnect Terminal Sessions
        print("\n[9] Disconnecting terminal sessions cleanly via /Disconnect...")
        if master_guid:
            disc_m = await demo.disconnect(master_guid, api_key=api_key)
            print(f"    Master Terminal Cleanly Disconnected: {disc_m.unique_identifier} (Lifetime: {disc_m.lifetime_seconds}s)")
        if slave_guid:
            disc_s = await demo.disconnect(slave_guid, api_key=api_key)
            print(f"    Slave Terminal Cleanly Disconnected:  {disc_s.unique_identifier} (Lifetime: {disc_s.lifetime_seconds}s)")

        await copier.close()
        print("\n=== PyCopier Trade Replication Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(main())
