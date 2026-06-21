#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def run_build_helper(fixture: dict, **overrides: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    with tempfile.TemporaryDirectory(prefix="ios-note-taker-build-helper-") as directory:
        temporary_root = Path(directory)
        bin_directory = temporary_root / "bin"
        bin_directory.mkdir()
        fixture_path = temporary_root / "devices.json"
        fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
        invocation_path = temporary_root / "xcodebuild-arguments.txt"

        write_executable(
            bin_directory / "xcrun",
            """#!/bin/sh
set -eu
[ "$*" = "simctl list devices available -j" ]
cat "$SIMULATOR_FIXTURE"
""",
        )
        write_executable(
            bin_directory / "xcodebuild",
            """#!/bin/sh
set -eu
printf '%s\n' "$@" > "$XCODEBUILD_ARGUMENTS"
""",
        )

        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{bin_directory}:{environment['PATH']}",
                "SIMULATOR_FIXTURE": str(fixture_path),
                "XCODEBUILD_ARGUMENTS": str(invocation_path),
                **overrides,
            }
        )
        result = subprocess.run(
            [str(ROOT / "build.sh")],
            cwd=temporary_root,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        arguments = (
            invocation_path.read_text(encoding="utf-8").splitlines()
            if invocation_path.exists()
            else []
        )
        return result, arguments


def fixture() -> dict:
    return {
        "devices": {
            "com.apple.CoreSimulator.SimRuntime.iOS-17-5": [
                {"name": "iPhone 15", "udid": "OLD-IPHONE", "isAvailable": True}
            ],
            "com.apple.CoreSimulator.SimRuntime.iOS-18-2": [
                {"name": "iPad Pro", "udid": "NEW-IPAD", "isAvailable": True},
                {"name": "iPhone 16 Pro", "udid": "NEW-IPHONE", "isAvailable": True},
                {"name": "iPhone 16", "udid": "UNAVAILABLE", "isAvailable": False},
            ],
        }
    }


def test_selects_latest_available_iphone_and_preserves_build_authority() -> None:
    result, arguments = run_build_helper(fixture())

    assert result.returncode == 0, result.stdout + result.stderr
    assert arguments == [
        "-project",
        str(ROOT / "NoteTaker.xcodeproj"),
        "-scheme",
        "NoteTaker",
        "-destination",
        "platform=iOS Simulator,id=NEW-IPHONE",
        "-sdk",
        "iphonesimulator",
        "-configuration",
        "Debug",
        "build",
    ]


def test_name_override_resolves_on_latest_matching_runtime() -> None:
    simulator_fixture = fixture()
    simulator_fixture["devices"]["com.apple.CoreSimulator.SimRuntime.iOS-18-2"].append(
        {"name": "iPhone 15", "udid": "NEW-NAMED-IPHONE", "isAvailable": True}
    )

    result, arguments = run_build_helper(simulator_fixture, SIMULATOR_NAME="iPhone 15")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "platform=iOS Simulator,id=NEW-NAMED-IPHONE" in arguments


def test_fails_clearly_without_an_available_iphone() -> None:
    result, arguments = run_build_helper(
        {
            "devices": {
                "com.apple.CoreSimulator.SimRuntime.iOS-18-2": [
                    {"name": "iPad Pro", "udid": "ONLY-IPAD", "isAvailable": True}
                ]
            }
        }
    )

    assert result.returncode != 0
    assert result.stderr.strip() == "No available iPhone simulator found."
    assert arguments == []


if __name__ == "__main__":
    test_selects_latest_available_iphone_and_preserves_build_authority()
    test_name_override_resolves_on_latest_matching_runtime()
    test_fails_clearly_without_an_available_iphone()
    print("build.sh simulator selection contract passed (3 cases).")
