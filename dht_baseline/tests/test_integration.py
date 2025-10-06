# tests/test_integration.py
import time
import pytest
from src.node.node import Node
from src.network.client import rpc_call

PORT_A = 9300
PORT_B = 9301

@pytest.fixture(scope="function")
def two_node_ring():
    node_a = Node("127.0.0.1", PORT_A)
    node_a.start()
    time.sleep(0.2)

    node_b = Node("127.0.0.1", PORT_B, bootstrap=f"127.0.0.1:{PORT_A}")
    node_b.start()
    # allow a bit of time for join/stabilize
    time.sleep(1.2)

    yield node_a, node_b

    # teardown
    node_a.stop()
    node_b.stop()
    time.sleep(0.1)

def test_put_get_between_two_nodes(two_node_ring):
    node_a, node_b = two_node_ring

    # do put via node A using Node.put (which routes to successor)
    resp_put = node_a.put("integration-key", "integration-value")
    assert resp_put is not None
    assert resp_put.get("type") == "ok"

    # try reading from node B (which may forward to successor)
    resp_get = node_b.get("integration-key")
    # In baseline, get returns {"type": "ok", "value": ...}
    assert resp_get is not None
    assert resp_get.get("type") == "ok"
    assert resp_get.get("value") == "integration-value"
