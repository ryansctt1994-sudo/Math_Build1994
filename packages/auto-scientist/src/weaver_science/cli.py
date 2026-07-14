from __future__ import annotations

import argparse
import json
from pathlib import Path

from .proof import LeanChecker


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="weaver-science")
    commands = parser.add_subparsers(required=True)
    proof = commands.add_parser("check-lean")
    proof.add_argument("path", type=Path)
    args = parser.parse_args(argv)

    result = LeanChecker().check(args.path.read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "status": result.status.value,
                "verified": result.verified,
                "checker": result.checker,
                "exit_code": result.exit_code,
                "stdout_hash": result.stdout_hash,
                "stderr_hash": result.stderr_hash,
                "diagnostics": result.diagnostics,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())

