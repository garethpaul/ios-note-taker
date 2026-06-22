#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import List, Tuple, Union


ROOT = Path(__file__).resolve().parents[1]


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def python39_interpreter() -> str:
    candidates = ["/usr/bin/python3", sys.executable]
    for candidate in candidates:
        result = subprocess.run(
            [candidate, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode == 0 and result.stdout.strip() == "3.9":
            return candidate
    raise AssertionError("Python 3.9 interpreter unavailable for compatibility checks")


def run_with_python39(source: str, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [python39_interpreter(), "-c", source, *arguments],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_source_remains_python_39_compatible() -> None:
    for python_path in sorted((ROOT / "scripts").glob("*.py")):
        result = run_with_python39(
            "import runpy, sys; runpy.run_path(sys.argv[1], run_name='python39_compatibility_check')",
            str(python_path),
        )
        assert result.returncode == 0, f"{python_path}: {result.stderr}"

    supported = run_with_python39(
        "Alias = dict[str, int]\n"
        "def supported(value: list[str]) -> dict[str, int]:\n    return {}\n"
    )
    assert supported.returncode == 0, supported.stderr

    annotated_union = run_with_python39(
        "def incompatible(value: dict | str):\n    pass\n"
    )
    assert annotated_union.returncode != 0
    assert "TypeError" in annotated_union.stderr

    alias_union = run_with_python39(
        "Alias = dict | str\n"
    )
    assert alias_union.returncode != 0
    assert "TypeError" in alias_union.stderr


def run_build_helper(
    fixture: Union[dict, str],
    *,
    xcrun_status: int = 0,
    **overrides: str,
) -> Tuple[subprocess.CompletedProcess, List[str]]:
    with tempfile.TemporaryDirectory(prefix="ios-note-taker-build-helper-") as directory:
        temporary_root = Path(directory)
        bin_directory = temporary_root / "bin"
        bin_directory.mkdir()
        fixture_path = temporary_root / "devices.json"
        fixture_path.write_text(
            fixture if isinstance(fixture, str) else json.dumps(fixture),
            encoding="utf-8",
        )
        invocation_path = temporary_root / "xcodebuild-arguments.txt"

        write_executable(
            bin_directory / "xcrun",
            """#!/bin/sh
set -eu
[ "$*" = "simctl list devices available -j" ]
cat "$SIMULATOR_FIXTURE"
exit "$XCRUN_STATUS"
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
        environment.pop("SIMULATOR_NAME", None)
        environment.update(
            {
                "PATH": f"{bin_directory}:{environment['PATH']}",
                "SIMULATOR_FIXTURE": str(fixture_path),
                "XCODEBUILD_ARGUMENTS": str(invocation_path),
                "XCRUN_STATUS": str(xcrun_status),
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


def test_preserves_xcrun_failure_before_parsing_valid_json() -> None:
    result, arguments = run_build_helper(fixture(), xcrun_status=42)

    assert result.returncode == 42
    assert result.stderr.strip() == "Unable to list available iOS simulators."
    assert arguments == []


def test_rejects_malformed_discovery_json_before_building() -> None:
    result, arguments = run_build_helper("{not-json")

    assert result.returncode != 0
    assert result.stderr.strip() == "Unable to parse available iOS simulators: invalid JSON."
    assert arguments == []


def test_rejects_missing_discovery_fields_before_building() -> None:
    missing_fields = [
        {"runtimes": {}},
        {
            "devices": {
                "com.apple.CoreSimulator.SimRuntime.iOS-18-2": [
                    {"name": "iPhone 16 Pro", "isAvailable": True}
                ]
            }
        },
    ]

    for simulator_fixture in missing_fields:
        result, arguments = run_build_helper(simulator_fixture)

        assert result.returncode != 0
        assert result.stderr.strip() == "Unable to parse available iOS simulators: missing required fields."
        assert arguments == []


def test_fails_clearly_for_an_unmatched_name_override() -> None:
    result, arguments = run_build_helper(fixture(), SIMULATOR_NAME="iPhone Retired")

    assert result.returncode != 0
    assert result.stderr.strip() == "No available iPhone simulator named 'iPhone Retired' found."
    assert arguments == []


def test_breaks_newest_runtime_ties_by_name_then_udid() -> None:
    simulator_fixture = fixture()
    simulator_fixture["devices"]["com.apple.CoreSimulator.SimRuntime.iOS-18-2"].extend(
        [
            {"name": "iPhone 16 Pro", "udid": "AAA-IPHONE", "isAvailable": True},
            {"name": "iPhone 16 Plus", "udid": "ZZZ-PLUS", "isAvailable": True},
            {"name": "iPhone 16 Plus", "udid": "AAA-PLUS", "isAvailable": True},
        ]
    )

    result, arguments = run_build_helper(simulator_fixture)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "platform=iOS Simulator,id=AAA-PLUS" in arguments


if __name__ == "__main__":
    test_source_remains_python_39_compatible()
    test_selects_latest_available_iphone_and_preserves_build_authority()
    test_name_override_resolves_on_latest_matching_runtime()
    test_fails_clearly_without_an_available_iphone()
    test_preserves_xcrun_failure_before_parsing_valid_json()
    test_rejects_malformed_discovery_json_before_building()
    test_rejects_missing_discovery_fields_before_building()
    test_fails_clearly_for_an_unmatched_name_override()
    test_breaks_newest_runtime_ties_by_name_then_udid()
    print("build.sh simulator selection contract passed (8 cases; Python 3.9 compatible).")
