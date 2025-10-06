# tests/test_nodes.py
import time
from src.node.node import Node
from src.node.utils import sha1_int, MOD

def test_node_id_and_addr():
    n = Node("127.0.0.1", 9100)
    assert isinstance(n.id, int)
    assert 0 <= n.id < MOD
    assert n.addr == "127.0.0.1:9100"

def test_storage_put_get_delete():
    n = Node("127.0.0.1", 9101)
    assert n.storage.get("missing") is None
    assert n.storage.put("k1", "v1") is True
    assert n.storage.get("k1") == "v1"
    assert n.storage.delete("k1") is True
    assert n.storage.get("k1") is None

def test_notify_and_predecessor_logic():
    n = Node("127.0.0.1", 9102)
    # initially None
    assert n.predecessor is None
    # simulate another node notifying this node
    n._handle_notify("127.0.0.1:9210")
    assert n.predecessor == "127.0.0.1:9210"
    # notifying with a node that should not replace predecessor:
    old_pred = n.predecessor
    n._handle_notify(old_pred)  # harmless
    assert n.predecessor == old_pred
