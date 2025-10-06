import socket
import threading
import selectors
from .protocol import decode_stream, encode_message
import traceback

class RPCServer:
    def __init__(self, host: str, port: int, handler):
        self.host = host
        self.port = port
        self.handler = handler  # function: (msg_dict, peer_addr) -> response_dict
        self._server = None
        self._running = False

    def start(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.host, self.port))
        self._server.listen()
        self._running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()
        print(f"[RPCServer] listening on {self.host}:{self.port}")

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self._server.accept()
                threading.Thread(target=self._handle_conn, args=(conn, addr), daemon=True).start()
            except Exception:
                traceback.print_exc()

    def _handle_conn(self, conn: socket.socket, addr):
        try:
            data = b""
            # read until EOF (client sends and closes)
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
            msgs = decode_stream(data)
            for m in msgs:
                try:
                    resp = self.handler(m, f"{addr[0]}:{addr[1]}")
                except Exception as e:
                    resp = {"type": "error", "error": str(e)}
                conn.sendall(encode_message(resp))
        except Exception:
            traceback.print_exc()
        finally:
            try:
                conn.close()
            except Exception as e:
                print(f"[RPCServer] Error closing connection: {e}")

    def stop(self):
        self._running = False
        try:
            self._server.close()
        except Exception as e:
            print(f"[RPCServer] Error closing server: {e}")
