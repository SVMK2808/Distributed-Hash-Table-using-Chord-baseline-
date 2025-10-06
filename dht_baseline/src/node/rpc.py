from ..network.client import rpc_call
from typing import Optional

def send_find_successor(peer_addr: str, id_int: int):
    msg = {"type": "find_successor", "id": str(id_int)}
    return rpc_call(peer_addr, msg)

def send_get_peer_info(peer_addr: str):
    msg = {"type": "peer_info"}
    return rpc_call(peer_addr, msg)

def send_put(peer_addr: str, key: str, value: str):
    return rpc_call(peer_addr, {"type": "put", "key": key, "value": value})

def send_get(peer_addr: str, key: str):
    return rpc_call(peer_addr, {"type": "get", "key": key})
