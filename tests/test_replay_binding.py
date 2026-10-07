import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "replay_build", Path(__file__).parents[1] / "scripts" / "replay_build.py"
)
replay_build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay_build)


@pytest.mark.parametrize("case", ["valid", "shell", "wrong_commit", "checkout", "drift", "missing_env", "invalid_commit"])
def test_replay_only_executes_bound_build(tmp_path, monkeypatch, case):
    commit = "a" * 40
    env = {"toolchain": "pinned", "lake_manifest_hash": "pinned"}
    env_hash = replay_build.environment_hash(env)
    receipt = {
        "evidence": {"command": "lake build MathBuild"},
        "provenance": {"commit": commit, "environment_hash": env_hash},
    }
    if case == "invalid_commit":
        receipt["provenance"]["commit"] = "--detach"
    elif case == "shell":
        receipt["evidence"]["command"] = "touch injected; lake build MathBuild"
    elif case == "drift":
        receipt["provenance"]["environment_hash"] = "sha256:other"
    elif case == "missing_env":
        receipt["provenance"].pop("environment_hash")
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt))
    monkeypatch.setattr(replay_build, "environment_snapshot", lambda: env)
    monkeypatch.setattr(replay_build, "current_commit", lambda: "b" * 40 if case == "wrong_commit" else commit)
    commands = []

    def run(argv):
        commands.append(argv)
        return (1, "", "checkout failed") if argv[0] == "git" else (0, "build passed", "")

    monkeypatch.setattr(replay_build, "run", run)
    result = replay_build.replay(path, tmp_path / "out", tmp_path / "matrix.json", case not in {"checkout", "invalid_commit"})
    builds = [cmd for cmd in commands if cmd[0] == "lake"]
    assert builds == ([["lake", "build", "MathBuild"]] if case == "valid" else [])
    assert result["replay_result"] == ("SUCCESS" if case == "valid" else "FAILURE")
    assert bool(result["refusal_reason"]) is (case != "valid")
    assert Path(result["output_path"]).is_file()
