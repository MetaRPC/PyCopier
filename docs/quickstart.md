# First request with Python

List your own copiers to check connectivity and identity without creating a terminal or placing a trade.

## 1. Install

Requires **Python 3.10+**. These instructions build from source; they do not assume a registry release exists.

```bash
git clone https://github.com/MetaRPC/PyCopier.git
cd PyCopier
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -e .
```

Java on Windows uses `;` for classpath separators. Run C++ builds in a Visual Studio developer shell. Activate your Python virtual environment before installing.

## 2. Set your owner key

=== "Bash"
    ```bash
    export MRPC_API_KEY='your-owner-key'
    ```
=== "PowerShell"
    ```powershell
    $env:MRPC_API_KEY = 'your-owner-key'
    ```

Use the real owner API key, not a broker password, terminal ID or `TRIAL`. Read [authentication](authentication.md) if access is refused.

## 3. Run

```bash
python examples/list.py
```

Source: [`examples/list.py`](https://github.com/MetaRPC/PyCopier/blob/main/examples/list.py).

```python
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
```

A successful empty list means this owner has no copiers. Treat failed requests as errors, not empty accounts.

## 4. Prepare a demo workflow

Read [the lifecycle guide](lifecycle.md), then [choose sizing](sizing.md). Existing replication examples under `examples/` are advanced integration examples: they may provision accounts and trade. Inspect them and their cleanup before running with disposable demos. List is the default starting point.
