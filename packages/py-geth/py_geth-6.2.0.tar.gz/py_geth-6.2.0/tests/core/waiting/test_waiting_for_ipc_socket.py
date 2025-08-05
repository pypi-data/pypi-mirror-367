import pytest

from flaky import (
    flaky,
)

from geth import (
    DevGethProcess,
)
from geth.utils.timeout import (
    Timeout,
)


def test_waiting_for_ipc_socket(base_dir):
    with DevGethProcess("testing", base_dir=base_dir) as geth:
        assert geth.is_running
        geth.wait_for_ipc(timeout=20)


@flaky(max_runs=3)
def test_timeout_waiting_for_ipc_socket(base_dir):
    with DevGethProcess("testing", base_dir=base_dir) as geth:
        assert geth.is_running
        with pytest.raises(Timeout):
            geth.wait_for_ipc(timeout=0.01)
