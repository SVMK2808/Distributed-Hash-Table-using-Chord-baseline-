import socket
from .protocol import encode_message, decode_stream
from typing import Optional
import socket

def rpc_call(addr: str, msg: dict, timeout: int = 3) -> Optional[dict]:
    host, port = addr.split(":")
    port = int(port)
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall(encode_message(msg))

            try:
                s.shutdown(socket.SHUT_WR)
            except Exception:
                pass
            # read response
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            if not data:
                return None
            msgs = decode_stream(data)
            return msgs[0] if msgs else None
    except Exception as e:
        return {"type": "error", "error": str(e)}
