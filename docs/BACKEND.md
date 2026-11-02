# コミュニティ投稿のバックエンド準備（Supabase）

方式：**匿名ログインで開始**（メール・Google 登録は不要）。悪用が出たら Apple でのサインインに切り替えます。
投稿は「審査待ち」で保存され、あなたが「審査して」と頼んだときに私が確認（不適切な内容・答えの正しさ）して、通ったものだけ公開します。

## あなたにお願いする作業

1. https://supabase.com でプロジェクトを作成（リージョンは Tokyo 推奨）。
2. **Authentication → Sign In / Providers → Anonymous Sign-Ins** を ON。
3. **SQL Editor** に `backend/schema.sql` の中身を貼って実行。
4. （審査は私が手動で行うため、Anthropic API キーも Edge Function も Webhook も不要です。）
5. **Project Settings → API** の **Project URL** と **anon public key** を私に教えてください
   （どちらも公開前提の値で、チャットに貼って問題ありません。service_role キーは絶対に貼らないでください）。

## 仕組み

- 投稿は必ず `pending` で保存 → 私が審査 → `approved`（公開）または `rejected`（理由つき）。
- 公開済みの問題と自分の投稿だけが読めます。審査結果は投稿者本人が書き換えられません。
- 通報が3人から来ると自動で非公開（`flagged`）。ブロック機能とアカウント削除（`delete_my_data`）も用意済み。

## App Store 審査向けの注意

- ユーザー投稿を扱うため、通報・ブロック・アプリ内でのデータ削除が必須（アプリ側に実装します）。
- プライバシーポリシーの URL が必要です（Premium 課金と共通）。
- 審査を私が手動で行うため、API 代はかかりません（Supabase の無料枠のみ）。
- 審査のときだけ、Supabase のアクセストークンをこのセッションの環境変数で渡してもらいます。
