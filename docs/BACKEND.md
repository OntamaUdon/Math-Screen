# コミュニティ投稿のバックエンド準備（Supabase）

方式：**匿名ログインで開始**（メール・Google 登録は不要）。悪用が出たら Apple でのサインインに切り替えます。
投稿は AI が審査（不適切な内容も確認）して、通ったものだけ公開されます。

## あなたにお願いする作業

1. https://supabase.com でプロジェクトを作成（リージョンは Tokyo 推奨）。
2. **Authentication → Sign In / Providers → Anonymous Sign-Ins** を ON。
3. **SQL Editor** に `backend/schema.sql` の中身を貼って実行。
4. Anthropic API キーを用意し、Supabase の **Edge Functions → Secrets** に `ANTHROPIC_API_KEY` として登録
   （チャットには貼らないでください）。
5. Edge Function `review-problem` を作成し、`backend/functions/review-problem/index.ts` の中身を貼って Deploy。
   - 「Verify JWT」は OFF にしてください（Database Webhook から呼ぶため）。
6. **Database → Webhooks** で新規作成：テーブル `community_problems`、イベント `Insert`、
   送り先は Edge Function の `review-problem`。
7. **Project Settings → API** の **Project URL** と **anon public key** を私に教えてください
   （どちらも公開前提の値で、チャットに貼って問題ありません。service_role キーは絶対に貼らないでください）。

## 仕組み

- 投稿は必ず `pending` で保存 → Webhook で AI が審査 → `approved`（公開）または `rejected`（理由つき）。
- 公開済みの問題と自分の投稿だけが読めます。審査結果は投稿者本人が書き換えられません。
- 通報が3人から来ると自動で非公開（`flagged`）。ブロック機能とアカウント削除（`delete_my_data`）も用意済み。

## App Store 審査向けの注意

- ユーザー投稿を扱うため、通報・ブロック・アプリ内でのデータ削除が必須（アプリ側に実装します）。
- プライバシーポリシーの URL が必要です（Premium 課金と共通）。
- AI 審査の費用は Anthropic API の従量課金です。投稿が増えたら上限を設定しましょう。
