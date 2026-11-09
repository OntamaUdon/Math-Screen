#!/usr/bin/env bash
# ロックの動きを、エミュレーターの上で自動で確かめる（GitHub Actions から呼ぶ）。
# 1. 見守りをオンにして、「設定」アプリに 1分のルールを作る
# 2. 「設定」アプリを1分少し使う → その上に問題が出るか
# 3. 問題を閉じる → ホームに戻るか。もう一度開く → また問題が出るか
# 4. わざとまちがえる → 「不正解」と出るか
# 5. 端末に PIN を付けて、画面を消して、つける → ロック画面の上に問題が出るか（共有のボタンは出さない）
# 6. ロック画面の上で正しく答える → PIN → 「設定」アプリに戻れるか、記録に残るか
# 7. また1分使う → もう一度ロックされるか → 緊急解除で戻れるか
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
# 見守りのサービスが動き出すまで待つ（動き出すと、診断のメモが残る）
for i in $(seq 1 30); do
  adb shell run-as $PKG cat shared_prefs/qlock.xml 2>/dev/null | grep -q 'diagNote.service' && break
  sleep 1
done
echo "  見守りが動き出すまで：約${i}秒"
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

# 4. まちがえた答え（problems.json から正解を読んで、わざとまちがえる）
answer(){ # $1 = right / wrong
  dump
  python3 android/tools/answer.py "$OUT/ui.xml" mathscreen/Resources/problems.json "$1" > "$OUT/keys.txt" || { echo "  （問題が見つからない）"; return 1; }
  while read -r k; do tap "$k" exact || return 1; done < "$OUT/keys.txt"
}
answer wrong
shot 3-wrong
if has "不正解" || has "ちがうみたい"; then ok "まちがえると「不正解」と出た"; else ng "まちがえたのに「不正解」が出ない"; fi

# 5. ロック画面の上
adb shell locksettings set-pin 1234 >/dev/null
adb shell input keyevent KEYCODE_SLEEP; sleep 3
adb shell input keyevent KEYCODE_WAKEUP; sleep 5
shot 4-lockscreen
KG=$(adb shell dumpsys window | grep -iE "keyguardShowing|isKeyguardShowing|mShowingLockscreen" | head -3 | tr -d '\r')
if top | grep -q ChallengeActivity; then ok "ロック中に画面をつけると、ロック画面の上に問題が出た（$KG）"; else ng "画面をつけても問題が出ない：$(top)"; fi
if has "この問題を共有する" || has "分からない"; then ng "ロック画面の上なのに、共有のボタンが出ている"; else ok "ロック画面の上では、共有のボタンを出さない"; fi

# 6. ロック画面の上で正しく答える → 端末の PIN → 設定アプリに戻る
answer right
shot 5-right
if has "解除してアプリに戻る"; then ok "正しく答えると「解除してアプリに戻る」が出た"; else ng "正解のあとのボタンが出ない"; fi
SOLVED=0; tap "解除してアプリに戻る" exact && SOLVED=1
sleep 2
adb shell input text 1234; adb shell input keyevent KEYCODE_ENTER; sleep 4
shot 6-after-solve
if [ "$SOLVED" = 1 ] && top | grep -q "$TARGET"; then ok "正解して解除すると、設定アプリに戻れた"; else ng "正解して解除したあとの画面：$(top)"; fi
PREFS=$(adb shell run-as $PKG cat shared_prefs/qlock.xml 2>/dev/null | tr -d '\r')
if echo "$PREFS" | grep -q 'unlocks&quot;:1\|unlocks\\":1'; then ok "「問題で解除」が記録に残った"; else ng "「問題で解除」の記録が見つからない"; fi

# 7. もう一度1分使うと、またロックされる → 緊急解除
sleep 75
shot 7-relock
if top | grep -q ChallengeActivity; then ok "解除のあと、また1分使うと、もう一度ロックされた"; else ng "2回目のロックがかからない：$(top)"; fi
tap "緊急解除" exact || true
tap "緊急解除する" exact || true
sleep 3
shot 8-after-emergency
if top | grep -q "$TARGET"; then ok "緊急解除のあと、設定アプリに戻れた"; else ng "緊急解除のあとの画面：$(top)"; fi
PREFS=$(adb shell run-as $PKG cat shared_prefs/qlock.xml 2>/dev/null | tr -d '\r')
if echo "$PREFS" | grep -q '<set name="locked" />' || ! echo "$PREFS" | grep -q 'name="locked"'; then ok "ロックが外れた（保存データ）"; else ng "ロックが残っている"; fi
if echo "$PREFS" | grep -q 'emergencyUnlocks&quot;:1\|emergencyUnlocks\\":1'; then ok "緊急解除が記録に残った"; else ng "緊急解除の記録が見つからない"; fi

adb shell locksettings clear --old 1234 >/dev/null 2>&1 || true
echo "---- 診断のメモ ----"
echo "$PREFS" | grep -o 'diagNote[^<]*<' | head
echo "---- 見守りのログ ----"
adb logcat -d -s Qlock:D | tail -60
echo "---- アプリのエラー（あれば） ----"
adb logcat -d -t 2000 AndroidRuntime:E '*:S' | tail -40
for f in "$OUT"/*.png; do echo "==BEGIN $(basename "$f")=="; base64 -w 0 "$f"; echo; echo "==END=="; done
echo "結果：OK $PASS、NG $FAIL"
[ "$FAIL" -eq 0 ]
