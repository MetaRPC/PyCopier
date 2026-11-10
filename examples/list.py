import asyncio
import os
from pycopier import CopierService

async def main():
    service = CopierService("copy.mrpc.pro:443", os.environ["MRPC_API_KEY"])
    try:
        result = await service.list()
        if not result.ok:
            raise RuntimeError(result.error)
        for copier in result.copiers:
            print(copier.id, copier.paused)
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(main())
