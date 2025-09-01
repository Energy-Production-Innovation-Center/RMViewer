import argparse
import sys
from pathlib import Path

sys.path.insert(0, ".")
sys.path.append(str(Path.cwd()).split("rmviewer")[0])

from rmviewer.handler import call_viewer


def _get_argument():
    parser = argparse.ArgumentParser(
        description="Representative Model Viewer",
    )
    parser.add_argument("--config_view", type=str, required=True, help="Path to config file (JSON)")
    return parser


def parse_args():
    parser = _get_argument()
    return parser.parse_args()


def main():
    args = parse_args()

    config_path = Path(args.config_view)
    if not config_path.exists():
        print(f"ERROR - Config file not found: {config_path}")
        sys.exit(1)

    call_viewer(config_path)


if __name__ == "__main__":
    main()
