# MetaRPC Python Trade Copier SDK

Authenticate, configure a master–follower relationship, inspect its state, pause and remove it.

**[Documentation](https://metarpc.github.io/PyCopier/) · [Quickstart](https://metarpc.github.io/PyCopier/quickstart/) · [Authentication](https://metarpc.github.io/PyCopier/authentication/) · [API reference](https://metarpc.github.io/PyCopier/reference/)**

## Install from source

Requires Python 3.10+.

```bash
git clone https://github.com/MetaRPC/PyCopier.git
cd PyCopier
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -e .
```

## First request

Set `MRPC_API_KEY` to your real owner API key in your environment, then run:

```bash
python examples/list.py
```

This List example is read-only: no account creation or trades. Java on Windows uses `;` instead of `:` in classpaths.

## Authentication

Every SDK call sends `ApiKey` (`apikey` in gRPC metadata). The gRPC body also carries `user_key`; the header does not replace it. `TRIAL` is not an owner key. Read the [verified transport contract](https://metarpc.github.io/PyCopier/authentication/).

## Scope and verification

Core operations: start · list · pause · remove (async). Advanced server features are distinguished from the supported wrapper surface. Review legacy replication examples before using them with disposable demos. Standard tests need no broker credentials.

See [testing and contributing](https://metarpc.github.io/PyCopier/testing/) for the regression suite, demo checklist and Pages build. Edit `docs/`; generated `site/` output is not source.
