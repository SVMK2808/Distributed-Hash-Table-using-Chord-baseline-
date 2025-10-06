# tests/test_network.py
import socket
from src.network.protocol import encode_message, decode_stream, parse_addr
from src.network.client import rpc_call

def test_encode_decode_roundtrip():
    msg = {"type": "ping", "payload": "hello"}
    encoded = encode_message(msg)
    decoded = decode_stream(encoded)
    assert isinstance(decoded, list)
    assert decoded[0] == msg

def test_parse_addr():
    host, port = parse_addr("127.0.0.1:8080")
    assert host == "127.0.0.1"
    assert port == 8080

def test_rpc_call_unreachable_port():
    # pick a port that is (likely) unused
    addr = "127.0.0.1:59999"
    resp = rpc_call(addr, {"type": "ping"}, timeout=1)
    # rpc_call returns a dict with type "error" on failure in our baseline
    assert resp is not None
    assert isinstance(resp, dict)
    assert resp.get("type") == "error" or "error" in resp
