import pytest
from unittest.mock import AsyncMock, patch
from pycopier import CopierService
from pycopier.account import CopierAccount
from pycopier.models import StartRequest, Account
from pycopier import copier_pb2 as pb

@pytest.mark.asyncio
async def test_every_rpc_authenticates_and_preserves_fields():
    service = CopierService("copy.mrpc.pro:443", "owner-test", "manager-test")
    service.stub.Start = AsyncMock(return_value=pb.StartReply(ok=True,copier_id="test"))
    service.stub.List = AsyncMock(return_value=pb.ListReply(ok=False,error="refused"))
    service.stub.Pause = AsyncMock(return_value=pb.SimpleReply(ok=True))
    service.stub.Remove = AsyncMock(return_value=pb.SimpleReply(ok=True))
    try:
        account = Account(user=9007199254740993,password="demo-only",server="Demo")
        assert (await service.start(StartRequest(master=account,slave=account,copy_sl=False,copy_tp=True))).ok
        failure = await service.list()
        assert not failure.ok and failure.error == "refused"
        await service.pause("test", False)
        await service.remove("test")
        for method in [service.stub.Start,service.stub.List,service.stub.Pause,service.stub.Remove]:
            args,kwargs=method.call_args
            assert dict(kwargs["metadata"])["apikey"] == "owner-test"
            assert kwargs["timeout"] > 0
            assert args[0].user_key == "owner-test"
        req=service.stub.Start.call_args.args[0]
        assert req.master.user==9007199254740993
        assert req.manager_key=="manager-test"
        assert not req.copy_sl and req.copy_tp
    finally: await service.close()

@pytest.mark.asyncio
async def test_log_stream_uses_server_data_not_sample_events():
    class Stream:
        def __aiter__(self): return self
        async def __anext__(self):
            if hasattr(self,"done"): raise StopAsyncIteration
            self.done=True
            return '{"CopierId":"test","SlaveTicket":"9007199254740993","Success":false,"ExceptionCode":"TEST"}'
    connection=AsyncMock()
    connection.__aenter__.return_value=Stream()
    service=CopierService("copy.mrpc.pro:443","owner-test")
    try:
        with patch("websockets.asyncio.client.connect",return_value=connection) as connect:
            logs=[item async for item in service.stream_trade_logs("test id")]
            assert len(logs)==1 and not logs[0].success
            assert logs[0].slave_ticket==9007199254740993
            assert logs[0].raw["ExceptionCode"]=="TEST"
            assert connect.call_args.kwargs["additional_headers"]["apikey"]=="owner-test"
            assert "test%20id" in connect.call_args.args[0]
    finally: await service.close()

@pytest.mark.parametrize("key", ["", "TRIAL", "trial", "a b", "x\r\nInjected: yes"])
def test_bad_keys(key):
    with pytest.raises(ValueError): CopierAccount("copy.mrpc.pro",key)
