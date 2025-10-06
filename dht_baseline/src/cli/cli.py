#!/usr/bin/env python3
import sys
from .parser import build_parser
from ..network.client import rpc_call

def main():
    parser = build_parser()
    args = parser.parse_args()

    addr = f"{args.host}:{args.port}"

    # For CLI simplicity, do direct RPC to local node.
    if args.cmd == "put":
        resp = rpc_call(addr, {"type": "put", "key": args.key, "value": args.value})
        print(resp)
    elif args.cmd == "get":
        resp = rpc_call(addr, {"type": "get", "key": args.key})
        print(resp)
    elif args.cmd == "join":
        # If local node exposes a join endpoint, call it; otherwise call bootstrap to find successor of local id.
        # Here we call bootstrap with a join-intent message (bootstrap node will handle find_successor).
        resp = rpc_call(args.bootstrap, {"type": "peer_info"})
        print(resp)
        # Note: The actual join is normally performed by starting a Node with bootstrap arg.
        print(f"To join, start your node with --join {args.bootstrap}")
    elif args.cmd == "info":
        resp = rpc_call(addr, {"type": "peer_info"})
        print(resp)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
