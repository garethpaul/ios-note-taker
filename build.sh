#!/bin/sh

set -eu

ROOT=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)

if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild unavailable; skipping Xcode build on this host."
    exit 0
fi

if ! command -v xcrun >/dev/null 2>&1; then
    echo "xcrun unavailable; cannot select an iOS Simulator." >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 unavailable; cannot select an iOS Simulator." >&2
    exit 1
fi

devices_json=$(mktemp "${TMPDIR:-/tmp}/ios-note-taker-simulators.XXXXXX")
cleanup() {
    rm -f "$devices_json"
}
trap cleanup 0 HUP INT TERM

if xcrun simctl list devices available -j > "$devices_json"; then
    :
else
    xcrun_status=$?
    echo "Unable to list available iOS simulators." >&2
    exit "$xcrun_status"
fi

simulator_udid=$(python3 -c '
import json
import os
import re
import sys

requested_name = os.environ.get("SIMULATOR_NAME", "")
candidates = []
try:
    with open(sys.argv[1], encoding="utf-8") as devices_file:
        discovery = json.load(devices_file)
except (OSError, json.JSONDecodeError):
    raise SystemExit("Unable to parse available iOS simulators: invalid JSON.")
if not isinstance(discovery, dict) or not isinstance(discovery.get("devices"), dict):
    raise SystemExit("Unable to parse available iOS simulators: missing required fields.")
runtimes = discovery["devices"]
for runtime, devices in runtimes.items():
    if not isinstance(runtime, str) or not isinstance(devices, list):
        raise SystemExit("Unable to parse available iOS simulators: missing required fields.")
    match = re.search(r"\.iOS-(\d+)-(\d+)(?:-(\d+))?$", runtime)
    if not match:
        continue
    version = tuple(int(part or 0) for part in match.groups())
    for device in devices:
        if (not isinstance(device, dict) or
                not isinstance(device.get("name"), str) or
                not isinstance(device.get("udid"), str) or
                not isinstance(device.get("isAvailable"), bool)):
            raise SystemExit("Unable to parse available iOS simulators: missing required fields.")
        name = device["name"]
        if (device.get("isAvailable") and name.startswith("iPhone") and
                (not requested_name or name == requested_name)):
            candidates.append((version, name, device["udid"]))

if not candidates:
    suffix = f" named {requested_name!r}" if requested_name else ""
    raise SystemExit(f"No available iPhone simulator{suffix} found.")

latest_version = max(version for version, _, _ in candidates)
_, simulator_udid = min(
    (name, udid)
    for version, name, udid in candidates
    if version == latest_version
)
print(simulator_udid)
' "$devices_json")

xcodebuild -project "$ROOT/NoteTaker.xcodeproj" \
           -scheme "NoteTaker" \
           -destination "platform=iOS Simulator,id=$simulator_udid" \
           -sdk iphonesimulator \
           -configuration "Debug" \
           build
