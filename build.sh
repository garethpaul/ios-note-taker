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

simulator_udid=$(xcrun simctl list devices available -j | python3 -c '
import json
import os
import re
import sys

requested_name = os.environ.get("SIMULATOR_NAME", "")
candidates = []
for runtime, devices in json.load(sys.stdin)["devices"].items():
    match = re.search(r"\.iOS-(\d+)-(\d+)(?:-(\d+))?$", runtime)
    if not match:
        continue
    version = tuple(int(part or 0) for part in match.groups())
    for device in devices:
        name = device.get("name", "")
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
')

xcodebuild -project "$ROOT/NoteTaker.xcodeproj" \
           -scheme "NoteTaker" \
           -destination "platform=iOS Simulator,id=$simulator_udid" \
           -sdk iphonesimulator \
           -configuration "Debug" \
           build
