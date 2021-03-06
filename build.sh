#!/bin/sh

set -eu

function ci_build() {
    NAME=$1
    xcodebuild -project "NoteTaker.xcodeproj" \
               -scheme "NoteTaker" \
               -destination "platform=iOS Simulator,name=${NAME}" \
               -sdk iphonesimulator \
               -configuration "Debug" \
               build
}


ci_build "iPhone 5"
