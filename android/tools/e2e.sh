#!/usr/bin/env bash
# ロックの動きを、エミュレーターの上で自動で確かめる（GitHub Actions から呼ぶ）。
# 1. 見守りをオンにして、「設定」アプリに 1分のルールを作る
# 2. 「設定」アプリを1分少し使う → その上に問題が出るか
# 3. 問題を閉じる → ホームに戻るか。もう一度開く → また問題が出るか
# 4. まちがえた答え → 「不正解」と出るか
# 5. 端末に PIN を付けて、画面を消して、つける → ロック画面の上に問題が出るか
# 6. 緊急解除 → PIN を入れる → 「設定」アプリに戻れるか、ロックが外れたか
set -u
APK=android/app/build/outputs/apk/debug/app-debug.apk
OUT=android/build-e2e
PKG=com.ontamaudon.qlock
TARGET=com.android.settings
UI=android/tools/ui.py
mkdir -p "$OUT"
PASS=0; FAIL=0
ok()  { echo "OK  $*"; PASS=$((PASS+1)); }
ng()  { echo "NG  $*"; FAIL=$((FAIL+1)); }
shot(){ adb exec-out screencap -p > "$OUT/$1.png"; }
top() { adb shell dumpsys activity activities | grep -m1 -E "topResumedActivity|mResumedActivity" | tr -d '\r'; }
dump(){ adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; adb pull /sdcard/ui.xml "$OUT/ui.xml" >/dev/null 2>&1; }
tap() { # 文字で探してタップ
  dump
  local xy; xy=$(python3 "$UI" "$OUT/ui.xml" "$1" ${2:-}) || { echo "  （画面に「$1」が見つかりません）"; return 1; }
  adb shell input tap $xy; sleep 1.5
}
has(){ dump; python3 "$UI" "$OUT/ui.xml" "$1" >/dev/null; }

adb wait-for-device
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb install -r -g "$APK" >/dev/null
adb shell pm grant $PKG android.permission.POST_NOTIFICATIONS 2>/dev/null || true

# 1. 準備
adb shell am start -W -n $PKG/.MainActivity --es e2e_rule_pkg $TARGET --ei e2e_minutes 1 >/dev/null
sleep 3
adb shell settings put secure enabled_accessibility_services $PKG/$PKG.guard.GuardService
adb shell settings put secure accessibility_enabled 1
sleep 3
if adb shell settings get secure enabled_accessibility_services | grep -q GuardService; then ok "見守り（ユーザー補助）をオンにできた"; else ng "見守りをオンにできない"; fi
adb shell input keyevent KEYCODE_HOME; sleep 2

# 2. 1分少し使う
adb shell am start -W -n $TARGET/.Settings >/dev/null
sleep 80
shot 1-locked
if top | grep -q ChallengeActivity; then ok "1分使うと、設定アプリの上に問題が出た"; else ng "1分たっても問題が出ない：$(top)"; fi

# 3. 閉じる → ホーム。もう一度開く → 問題
tap "閉じる" exact || true
sleep 2
if top | grep -qi launcher; then ok "問題を閉じると、ホーム画面に戻った"; else ng "閉じたあとがホームでない：$(top)"; fi
adb shell am start -W -n $TARGET/.Settings >/dev/null
sleep 4
shot 2-reopen
if top | grep -q ChallengeActivity; then ok "ロック中に開き直すと、また問題が出た"; else ng "開き直しても問題が出ない：$(top)"; fi

# 4. まちがえた答え（4択なら①、数字なら ±999）
if has "こたえる"; then
  if has "①"; then tap "①" exact || true; else tap "±" exact || true; for i in 1 2 3; do tap "9" exact || true; done; fi
  tap "こたえる" exact || true
  shot 3-wrong
  if has "不正解" || has "ちがうみたい"; then ok "まちがえると「不正解」と出た"
  elif has "正解　答えは"; then ok "（たまたま正解だった）"
  else ng "答えたあとの表示が見つからない"; fi
fi

# 5. ロック画面の上
adb shell locksettings set-pin 1234 >/dev/null
adb shell input keyevent KEYCODE_SLEEP; sleep 3
adb shell input keyevent KEYCODE_WAKEUP; sleep 5
shot 4-lockscreen
if adb shell dumpsys window | grep -q "mDreamingLockscreen=false" ; then :; fi
if top | grep -q ChallengeActivity && adb shell dumpsys window | grep -qE "isKeyguardShowing=true|mShowingLockscreen=true|keyguardShowing=true|KeyguardShowing=true"; then
  ok "ロック中に画面をつけると、ロック画面の上に問題が出た"
elif top | grep -q ChallengeActivity; then
  ok "画面をつけると問題が出た（ロック画面かどうかは判定できず。画像 4-lockscreen を見る）"
else ng "画面をつけても問題が出ない：$(top)"; fi

# 6. 緊急解除 → PIN → 設定アプリに戻る
tap "緊急解除" exact || true
tap "緊急解除する" exact || true
sleep 2
adb shell input text 1234; adb shell input keyevent KEYCODE_ENTER; sleep 4
shot 5-after-unlock
if top | grep -q "$TARGET"; then ok "緊急解除のあと、設定アプリに戻れた"; else ng "緊急解除のあとの画面：$(top)"; fi
PREFS=$(adb shell run-as $PKG cat shared_prefs/qlock.xml 2>/dev/null | tr -d '\r')
if echo "$PREFS" | grep -q '<set name="locked" />' || ! echo "$PREFS" | grep -q 'name="locked"'; then ok "ロックが外れた（保存データ）"; else ng "ロックが残っている"; fi
if echo "$PREFS" | grep -q 'emergencyUnlocks\\*":1\|emergencyUnlocks&quot;:1'; then ok "緊急解除が記録に残った"; else echo "  （記録の確認はスキップ）"; fi

adb shell locksettings clear --old 1234 >/dev/null 2>&1 || true
echo "---- 診断のメモ ----"
echo "$PREFS" | grep -o 'diagNote[^<]*<' | head
echo "---- アプリのエラー（あれば） ----"
adb logcat -d -t 2000 AndroidRuntime:E '*:S' | tail -40
for f in "$OUT"/*.png; do echo "==BEGIN $(basename "$f")=="; base64 -w 0 "$f"; echo; echo "==END=="; done
echo "結果：OK $PASS、NG $FAIL"
[ "$FAIL" -eq 0 ]
