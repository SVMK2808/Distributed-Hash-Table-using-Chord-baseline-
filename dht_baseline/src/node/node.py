import threading
import time
from .storage import Storage
from .utils import sha1_int, id_in_interval, M_BITS, MOD
from ..network.server import RPCServer
from ..network.client import rpc_call
from ..network.protocol import parse_addr
from typing import Optional

class Node:
    def __init__(self, host: str, port: int, bootstrap: Optional[str] = None):
        self.host = host
        self.port = port
        self.addr = f"{host}:{port}"
        self.id = sha1_int(self.addr) % MOD
        self.storage = Storage()

        # Chord-like pointers
        self.successor = self.addr  # initially self
        self.predecessor = None

        # RPC server
        self.server = RPCServer(host, port, self._rpc_handler)
        self._stabilize_thread = None
        self._stop = False

        # If bootstrap provided, join the ring
        self.bootstrap = bootstrap

    def start(self):
        self.server.start()
        # start stabilization background thread (naive)
        if self.bootstrap:
            joined = False
            for attempt in range(6):
                try:
                    self.join(self.bootstrap)
                    joined = True
                    break
                except Exception as e:
                    print("Join attempt failed:", e)
                    time.sleep(0.2)
            if not joined:
                print(f"[{self.addr}] warning: join attempts exhausted, running as standalone node")

        self._stabilize_thread = threading.Thread(target=self._stabilize_loop, daemon=True)
        self._stabilize_thread.start()

    def stop(self):
        self._stop = True
        self.server.stop()

    def _stabilize_loop(self):
        while not self._stop:
            try:
                self.stabilize()
            except Exception as e:
                print(f"[Node] Stabilize error: {e}")
            time.sleep(5)

    def join(self, bootstrap_addr: str):
        if bootstrap_addr == self.addr:
            return
        # ask bootstrap for successor of our id
        resp = rpc_call(bootstrap_addr, {"type": "find_successor", "id": str(self.id)})
        if resp is None:
            raise RuntimeError(f"join failed: no response from bootstrap {bootstrap_addr}")
        
        if resp.get("type") == "error":
            raise RuntimeError(f"join failed: bootstrap returned error: {resp.get('error')}")
        
        succ = resp.get("successor")
        if not succ:
            print(f"[join] unexpected bootstrap response: {resp}")
            raise RuntimeError("join failed: boostrap did not return successor")
        
        self.successor = succ
        print(f"[{self.addr}] joined ring. successor={self.successor}")

    def stabilize(self):
        # ask successor for its predecessor
        if self.successor == self.addr:
            return
        resp = rpc_call(self.successor, {"type": "get_predecessor"})
        if resp and resp.get("type") != "error":
            pred = resp.get("predecessor")
            if pred:
                pred_id = sha1_int(pred) % MOD
                if id_in_interval(pred_id, self.id, sha1_int(self.successor) % MOD):
                    self.successor = pred
        # notify successor about self
        rpc_call(self.successor, {"type": "notify", "node": self.addr})

    def _rpc_handler(self, msg: dict, peer: str):
        mtype = msg.get("type")
        if mtype == "peer_info":
            return {"type": "peer_info", "addr": self.addr, "id": str(self.id), "successor": self.successor, "predecessor": self.predecessor}
        if mtype == "find_successor":
            id_int = int(msg["id"])
            return self._handle_find_successor(id_int)
        if mtype == "get_predecessor":
            return {"type": "predecessor", "predecessor": self.predecessor}
        if mtype == "notify":
            node_addr = msg.get("node")
            return self._handle_notify(node_addr)
        if mtype == "put":
            key = msg.get("key")
            value = msg.get("value")
            self.storage.put(key, value)
            return {"type": "ok"}
        if mtype == "get":
            key = msg.get("key")
            val = self.storage.get(key)
            return {"type": "ok", "value": val}
        return {"type": "error", "error": "unknown message"}

    def _handle_find_successor(self, id_int: int):
        # simplified: if id in (self.id, successor.id] -> successor
        succ_id = sha1_int(self.successor) % MOD
        if id_in_interval(id_int, self.id, succ_id, inclusive_end=True):
            return {"type": "successor", "successor": self.successor}
        else:
            # forward to successor (naive routing)
            resp = rpc_call(self.successor, {"type": "find_successor", "id": str(id_int)})
            return resp if resp else {"type": "error", "error": "no response"}

    def _handle_notify(self, node_addr: str):
        # called by others to tell we might be their successor
        if self.predecessor is None:
            self.predecessor = node_addr
        else:
            pred_id = sha1_int(self.predecessor) % MOD
            node_id = sha1_int(node_addr) % MOD
            if id_in_interval(node_id, pred_id, self.id):
                self.predecessor = node_addr
        return {"type": "ok"}

    # convenience operations for CLI
    def put(self, key: str, value: str):
        # find responsible node then send put
        key_id = sha1_int(key) % MOD
        resp = rpc_call(self.addr, {"type": "find_successor", "id": str(key_id)})
        if resp and resp.get("type") == "successor":
            node = resp.get("successor")
            return rpc_call(node, {"type": "put", "key": key, "value": value})
        return {"type": "error", "error": "no successor"}

    def get(self, key: str):
        key_id = sha1_int(key) % MOD
        resp = rpc_call(self.addr, {"type": "find_successor", "id": str(key_id)})
        if resp and resp.get("type") == "successor":
            node = resp.get("successor")
            return rpc_call(node, {"type": "get", "key": key})
        return {"type": "error", "error": "no successor"}
