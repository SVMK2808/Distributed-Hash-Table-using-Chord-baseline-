import argparse

def build_parser():
    p = argparse.ArgumentParser(prog="dht-cli")
    p.add_argument("--host", default="127.0.0.1", help="node host")
    p.add_argument("--port", type=int, required=True, help="node port")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_put = sub.add_parser("put")
    p_put.add_argument("key")
    p_put.add_argument("value")

    p_get = sub.add_parser("get")
    p_get.add_argument("key")

    p_join = sub.add_parser("join")
    p_join.add_argument("--bootstrap", required=True, help="bootstrap addr host:port")

    p_info = sub.add_parser("info")

    return p
