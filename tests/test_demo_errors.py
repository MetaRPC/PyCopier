import io
import pytest
from pycopier.demo import _read_json

def test_http_200_error_is_not_empty_success():
    with pytest.raises(RuntimeError, match='MAX_TERMINALS_PER_POD_REACHED') as error:
        _read_json(io.BytesIO(b'{"error":{"errorCode":"MAX_TERMINALS_PER_POD_REACHED","stackTrace":"private trace"}}'))
    assert 'private trace' not in str(error.value)

def test_successful_empty_positions_remain_valid():
    assert _read_json(io.BytesIO(b'{"data":{"positionInfos":[]}}')) == {'data':{'positionInfos':[]}}
