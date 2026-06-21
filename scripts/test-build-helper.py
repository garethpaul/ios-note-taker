#!/usr/bin/env python3
import ast
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import List, Tuple, Union


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_GENERIC_NAMES = {"dict", "frozenset", "list", "set", "tuple", "type"}


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def python39_annotation_errors(source: str) -> List[str]:
    tree = ast.parse(source)
    annotations = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            annotations.extend(
                argument.annotation
                for argument in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                if argument.annotation is not None
            )
            if node.args.vararg and node.args.vararg.annotation is not None:
                annotations.append(node.args.vararg.annotation)
            if node.args.kwarg and node.args.kwarg.annotation is not None:
                annotations.append(node.args.kwarg.annotation)
            if node.returns is not None:
                annotations.append(node.returns)
        elif isinstance(node, ast.AnnAssign):
            annotations.append(node.annotation)

    errors = []
    for annotation in annotations:
        for node in ast.walk(annotation):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                errors.append("PEP 604 union")
            if isinstance(node, ast.Subscript):
                if isinstance(node.value, ast.Name) and node.value.id in RUNTIME_GENERIC_NAMES:
                    errors.append(f"runtime generic {node.value.id}")
                if (isinstance(node.value, ast.Attribute) and
                        isinstance(node.value.value, ast.Name) and
                        node.value.value.id == "subprocess" and
                        node.value.attr == "CompletedProcess"):
                    errors.append("runtime generic subprocess.CompletedProcess")
    return errors


def test_source_remains_python_39_compatible() -> None:
    for python_path in sorted((ROOT / "scripts").glob("*.py")):
        source = python_path.read_text(encoding="utf-8")
        assert python39_annotation_errors(source) == [], python_path

    assert "PEP 604 union" in python39_annotation_errors(
        "def incompatible(value: dict | str):\n    pass\n"
    )
    assert "runtime generic tuple" in python39_annotation_errors(
        "def incompatible() -> tuple[str, list[str]]:\n    pass\n"
    )


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
