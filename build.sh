#!/bin/sh

set -eu

if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild unavailable; skipping Xcode build on this host."
    exit 0
fi

ci_build() {
    NAME=$1
    xcodebuild -project "NoteTaker.xcodeproj" \
               -scheme "NoteTaker" \
               -destination "platform=iOS Simulator,name=${NAME}" \
               -sdk iphonesimulator \
               -configuration "Debug" \
               build
}


ci_build "${SIMULATOR_NAME:-iPhone 5}"
