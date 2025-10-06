import json
from typing import Tuple

def encode_message(msg: dict) -> bytes:
    # JSON message with newline delimiter
    return (json.dumps(msg) + "\n").encode()

def decode_stream(stream_bytes: bytes) -> list:
    # split by newline -> JSON messages
    lines = stream_bytes.decode().splitlines()
    msgs = []
    for line in lines:
        if not line.strip():
            continue
        try:
            msgs.append(json.loads(line))
        except Exception:
            # skip malformed
            continue
    return msgs

def parse_addr(addr: str) -> Tuple[str, int]:
    # addr like "127.0.0.1:8000"
    host, port = addr.split(":")
    return host, int(port)
