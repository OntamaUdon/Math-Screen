# 解くロック（Android 版）

iPhone 版（`mathscreen/`）と同じアプリを、Android 向けに作り直したものです。Kotlin と Jetpack Compose で書いています。

- 問題データ（`problems.json`）・単元（`units.json`）・KaTeX は、**ビルドのときに iPhone 版のフォルダからコピー**します。iPhone 版のファイルは変えません。問題を足すと、両方に入ります。
- ビルドは GitHub Actions（`.github/workflows/android.yml`）。push すると、デバッグ版の APK ができます。
- コミットメッセージに `[android-shots]` を入れると、エミュレーターで起動して、画面のスクリーンショットも撮ります。

## iPhone 版との違い

| | iPhone 版 | Android 版 |
|---|---|---|
| 問題を出すまで | ブロック画面 → 通知 → タップ → 問題 | **制限したアプリの上に、すぐ問題が出る** |
| 使った時間 | iOS が数える（10分の1ごとの目安） | アプリが数える（1分単位で表示） |
| ロック画面 | 何もできない | **ロック中に画面をつけると、ロック画面の上で問題に答えられる**（設定でオフにできる） |
| 制限できるもの | アプリ・カテゴリ・Web サイト | アプリ・アプリの種類（SNS・ゲームなど）。**Web サイトは制限できない** |
| 制限を外されないようにする | スクリーンタイムの仕組み | 弱い（設定からユーザー補助をオフにすれば、だれでも止められる） |
| 文字 | SF Rounded | M PLUS Rounded 1c（SF Rounded は Apple 以外で使えないため） |
| アイコン | SF Symbols | Material Symbols の、形の近いもの |
| 確認の小窓 | iOS の形 | Android 標準の形 |

## 確かめられたこと・まだのこと

`STATUS.md` にまとめています。

## フォルダ

```
app/src/main/java/com/ontamaudon/qlock/
  data/      問題・記録・出題の選び方・正答率の集計・保護者用設定
  guard/     ユーザー補助サービス（前に出ているアプリを見る）・時間の計測・通知
  billing/   Google Play の定期購入
  ui/        見た目（Theme.kt）と部品、画面
app/src/main/assets/   文字（M PLUS Rounded 1c）、Android 用の KaTeX の HTML
docs/      Google Play の手順、データ セーフティの答えの案
tools/     スクリーンショットを撮るスクリプト
```
