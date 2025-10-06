# src/config_loader.py
from pathlib import Path
import yaml  # pip install pyyaml
import sys

DEFAULTS = {
    "node": {
        "host": "127.0.0.1",
        "port": 8000,
        "m_bits": 160,
        "stabilization_interval": 5,
        "rpc_retry_interval": 1,
    },
    "network": {
        "rpc_timeout": 3,
        "listen_backlog": 32,
        "max_message_size": 65536,
    },
    "storage": {
        "persistence": False,
        "data_dir": "./data",
        "snapshot_interval": 30,
    },
    "logging": {
        "level": "INFO",
        "file": None,
    },
    "cli": {
        "default_host": "127.0.0.1",
        "default_port": 8000,
    },
    "testing": {
        "test_nodes": [],
    },
    "advanced": {
        "replication_factor": 1,
        "finger_table_size": 0,
    }
}

def load_config(path: str = "config/settings.yaml") -> dict:
    cfg_path = Path(path)
    cfg = {}
    if cfg_path.exists():
        with cfg_path.open("r") as f:
            try:
                cfg = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[config_loader] error parsing {path}: {e}", file=sys.stderr)
                raise
    else:
        print(f"[config_loader] warning: {path} not found, using defaults", file=sys.stderr)

    # deep-merge DEFAULTS <- cfg
    def deep_merge(a, b):
        out = dict(a)
        for k, v in b.items():
            if isinstance(v, dict) and k in out and isinstance(out[k], dict):
                out[k] = deep_merge(out[k], v)
            else:
                out[k] = v
        return out

    merged = deep_merge(DEFAULTS, cfg)

    # small validations
    node = merged["node"]
    if not isinstance(node.get("port"), int) or not (1 <= node["port"] <= 65535):
        raise ValueError("node.port must be an integer in 1..65535")

    if merged["network"]["rpc_timeout"] <= 0:
        raise ValueError("network.rpc_timeout must be > 0")

    return merged
