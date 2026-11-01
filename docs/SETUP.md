# Mac なしで TestFlight に配信するまでの手順

ビルドは GitHub Actions の Mac 環境で行い、そのまま TestFlight にアップロードします。
作業はすべてブラウザ（と iPhone）だけで完結します。

---

## 0. 全体の流れ

| # | やること | 場所 |
|---|---|---|
| 1 | App Group と App ID（4つ）を登録 | Apple Developer |
| 2 | Family Controls（配布用）の利用申請 | Apple Developer |
| 3 | App Store Connect にアプリを作成 | App Store Connect |
| 4 | API キーを作成 | App Store Connect |
| 5 | GitHub に Secrets を登録 | GitHub |
| 6 | ワークフローを実行 → TestFlight で受け取る | GitHub / iPhone |

> **大事な注意**
> スクリーンタイム機能（Family Controls）を **TestFlight / App Store で使うには Apple の許可（2.）が必要** です。
> 許可が下りるまでは、ワークフローを `screen_time = false` で実行すると、制限機能を外した版（問題・練習・記録などの画面は確認可）を TestFlight で受け取れます。

---

## 1. App Group と App ID を登録する

[Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/identifiers/list) を開きます。

### 1-1. App Group
1. 右上のプルダウンを **App Groups** にして「＋」
2. Description: `mathscreen`、Identifier: `group.com.mathscreen.mathscreen`

### 1-2. App ID（4つ）
「＋」→ **App IDs** → **App** で、以下の4つを登録します（Bundle ID は Explicit）。

| Description | Bundle ID |
|---|---|
| mathscreen | `com.mathscreen.mathscreen` |
| mathscreen Monitor | `com.mathscreen.mathscreen.monitor` |
| mathscreen Shield | `com.mathscreen.mathscreen.shieldconfig` |
| mathscreen Shield Action | `com.mathscreen.mathscreen.shieldaction` |

それぞれ Capabilities で次の2つにチェックします。
- **App Groups** → Configure で `group.com.mathscreen.mathscreen` を選択
- **Family Controls**（ここで有効になるのは開発用）

> Bundle ID は「アプリを世界で一意に見分けるための ID」です。アプリ本体と、ブロック画面などを担当する3つの拡張機能それぞれに必要です。

## 2. Family Controls（配布用）を申請する

1. [Family Controls Distribution の申請フォーム](https://developer.apple.com/contact/request/family-controls-distribution) を開く
2. **上の4つの Bundle ID すべて** について申請する（1つずつ申請が必要です）
3. 用途の説明例：
   > This app helps users reduce their own excessive smartphone use. When a user-selected app is used beyond a user-defined time limit, the app is shielded and the user must solve a math problem to continue. It uses FamilyControls with individual authorization, DeviceActivity for usage thresholds, and ManagedSettings for shields. Data stays on device.

許可されると、各 App ID の Capabilities に **Family Controls (Distribution)** が表示されます（数日〜数週間かかることがあります）。

## 3. App Store Connect にアプリを作成する

1. [App Store Connect](https://appstoreconnect.apple.com/apps) → 「＋」→ **新規 App**
2. プラットフォーム: iOS / 名前: `mathscreen`（他のアプリと重複していると使えません。その場合は「mathscreen - 数学で止める」など）/ 主言語: 日本語
3. バンドル ID: `com.mathscreen.mathscreen` / SKU: `mathscreen`

## 4. App Store Connect API キーを作成する

1. App Store Connect → **ユーザとアクセス** → **統合** → **App Store Connect API** → **チームキー**
2. 「＋」で生成。アクセスは **Admin**（クラウドで署名用証明書を自動作成するために必要）
3. 次の3つを控える
   - **キー ID**
   - **Issuer ID**（一覧の上部に表示）
   - **API キー（.p8 ファイル）** — ダウンロードは1回だけなので大切に保管

あわせて [Membership details](https://developer.apple.com/account#MembershipDetailsCard) で **Team ID**（10桁の英数字）を控えます。

## 5. GitHub に Secrets を登録する

リポジトリの **Settings → Secrets and variables → Actions → New repository secret** で4つ登録します。

| Name | 値 |
|---|---|
| `APPLE_TEAM_ID` | Team ID |
| `ASC_KEY_ID` | キー ID |
| `ASC_ISSUER_ID` | Issuer ID |
| `ASC_PRIVATE_KEY` | .p8 ファイルの中身をそのまま貼り付け（`-----BEGIN PRIVATE KEY-----` から `-----END PRIVATE KEY-----` まで） |

## 6. ビルドして TestFlight で受け取る

このリポジトリには作業ブランチしかなく、標準ブランチに TestFlight のワークフローがないため、Actions の「Run workflow」ボタンは出ません。次のどちらかで実行します。

- **A. 失敗した実行をやり直す（自分でできる）**：Actions タブ → **TestFlight** → 一覧の実行 → 右上の **Re-run all jobs**。Secrets を登録したあとは、これで新しい値が使われます。
- **B. Claude に頼む**：コミットメッセージに `[testflight]` を含めて push します。`[ui-only]` も含めると、スクリーンタイム機能(Family Controls)を外した版になります。

Family Controls の配布用許可が **まだ** のときは、`[ui-only]` の版（B）にします。A のやり直しは完全版なので、許可がないと署名で失敗します。

1. 10〜20 分ほどで完了。App Store Connect の **TestFlight** タブにビルドが表示されます（処理にさらに数分〜30分）
2. TestFlight → **内部テスト** にグループを作り、自分を追加
3. iPhone に **TestFlight** アプリを入れて、届いた招待からインストール

---

## うまくいかないとき

| 症状 | 原因と対処 |
|---|---|
| `Secret が足りません` | 5. の Secrets 名のつづりを確認 |
| `No profiles for 'com.mathscreen.mathscreen' were found` / Family Controls 関連のエラー | 配布用の許可がまだ。`screen_time = false` で実行する |
| `Cloud signing permission error` | API キーのアクセスが Admin になっていない |
| `No suitable application records were found` | 3. のアプリ作成が未完了、または Bundle ID が違う |
| ビルド番号の重複エラー | ワークフローをもう一度実行（実行番号がビルド番号になります） |

失敗したときは、Actions の実行結果ページ下部の **logs** をダウンロードすると詳細が見られます。
