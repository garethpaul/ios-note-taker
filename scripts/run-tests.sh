#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DERIVED_DATA=${DERIVED_DATA:-"${TMPDIR:-/tmp}/ios-note-taker-derived"}

if [ -n "${IOS_SIMULATOR_UDID:-}" ]; then
    simulator_udid=$IOS_SIMULATOR_UDID
else
    simulator_udid=$(xcrun simctl list devices available -j | python3 -c '
import json, sys
devices = json.load(sys.stdin)["devices"]
for runtime in sorted(devices, reverse=True):
    for device in devices[runtime]:
        if device.get("isAvailable") and device.get("name", "").startswith("iPhone"):
            print(device["udid"])
            raise SystemExit(0)
raise SystemExit("No available iPhone simulator found")
')
fi

xcrun simctl boot "$simulator_udid" 2>/dev/null || true
xcrun simctl bootstatus "$simulator_udid" -b

xcodebuild \
    -project "$ROOT/NoteTaker.xcodeproj" \
    -scheme NoteTakerTests \
    -destination "platform=iOS Simulator,id=$simulator_udid" \
    -derivedDataPath "$DERIVED_DATA" \
    -parallel-testing-enabled NO \
    CODE_SIGNING_ALLOWED=NO \
    test
