import asyncio
from pycopier import CopierService, DemoAccountClient, Account, StartRequest

async def main():
    print("=== PyCopier Quick Start ===")
    demo = DemoAccountClient("mt5.mrpc.pro:443")
    master = await demo.open_demo_account(first_name="Master")
    slave = await demo.open_demo_account(first_name="Slave")
    print(f"Master login: {master.login}, Slave login: {slave.login}")

    copier = CopierService("copy.mrpc.pro:443", user_key="YOUR_USER_KEY")
    req = StartRequest(
        user_key="YOUR_USER_KEY",
        master=Account(type="MT5", user=master.login, password=master.password, server=master.server),
        slave=Account(type="MT5", user=slave.login, password=slave.password, server=slave.server),
        risk_type="LotMultiplier",
        risk_value="1.5"
    )
    reply = await copier.start(req)
    print(f"Started copier: {reply.copier_id}")

    list_reply = await copier.list()
    print(f"Active copiers: {len(list_reply.copiers)}")

    await copier.pause(reply.copier_id, True)
    await copier.remove(reply.copier_id)
    await copier.close()
    print("Copier stopped and removed.")

if __name__ == "__main__":
    asyncio.run(main())
