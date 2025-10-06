#!/usr/bin/env python3
import argparse
import signal
import sys
from src.node.node import Node

def build_parser():
    p = argparse.ArgumentParser(prog="dht-node")
    p.add_argument("--host", default="127.0.0.1", help="host to bind")
    p.add_argument("--port", type=int, required=True, help="port to bind")
    p.add_argument("--join", help="bootstrap node addr host:port", default=None)
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    node = Node(args.host, args.port, bootstrap=args.join)
    node.start()

    def shutdown(signum, frame):
        print("\nShutting down node...")
        node.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep main thread alive
    print(f"Node running at {node.addr} with id {node.id}")
    while True:
        signal.pause()

if __name__ == "__main__":
    main()
