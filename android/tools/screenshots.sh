#!/usr/bin/env bash
# エミュレーターでアプリを起動して、画面ごとのスクリーンショットを撮る（GitHub Actions から呼ぶ）。
# 画面は本物。見本のデータだけを入れる（ScreenshotMode.kt）。
set -u
APK=android/app/build/outputs/apk/debug/app-debug.apk
OUT=android/build-screenshots
PKG=com.ontamaudon.qlock
mkdir -p "$OUT"
adb wait-for-device
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb install -r -g "$APK"
for scene in onboarding home book stats settings plan solve challenge; do
  adb shell pm clear "$PKG" >/dev/null
  adb shell pm grant "$PKG" android.permission.POST_NOTIFICATIONS 2>/dev/null || true
  adb shell am start -W -n "$PKG/.MainActivity" --es screenshot "$scene" >/dev/null
  sleep 10
  adb exec-out screencap -p > "$OUT/$scene.png"
  echo "撮影：$scene"
done
# 起動に失敗したときの手がかり
adb logcat -d -t 400 '*:E' > "$OUT/logcat-errors.txt" || true
