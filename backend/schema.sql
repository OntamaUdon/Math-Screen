-- 解くロック コミュニティ投稿用のテーブル（Supabase の SQL Editor に貼って実行）

create table if not exists public.community_problems (
  id           uuid primary key default gen_random_uuid(),
  author       uuid not null default auth.uid(),
  genre        text not null,                    -- 例: junior / math1a / eng_word / soc_hist / sci_bio
  difficulty   int  not null check (difficulty between 1 and 3),
  title        text not null check (char_length(title) <= 60),
  body         text not null check (char_length(body) <= 1000),   -- LaTeX 可
  plain        text not null check (char_length(plain) <= 1000),  -- 読み上げ・代替テキスト
  answer       text not null check (char_length(answer) <= 60),
  explanation  text not null default '' check (char_length(explanation) <= 1000),
  choices      jsonb,                            -- 4択のとき ["...","...","...","..."]
  hint         text check (hint is null or char_length(hint) <= 300),
  status       text not null default 'pending'
               check (status in ('pending','approved','rejected','flagged')),
  review_note  text,                             -- 審査コメント
  created_at   timestamptz not null default now()
);

create index if not exists community_problems_status_idx on public.community_problems (status, created_at desc);

create table if not exists public.problem_reports (
  id         uuid primary key default gen_random_uuid(),
  problem_id uuid not null references public.community_problems(id) on delete cascade,
  reporter   uuid not null default auth.uid(),
  reason     text not null check (char_length(reason) <= 300),
  created_at timestamptz not null default now(),
  unique (problem_id, reporter)
);

create table if not exists public.user_blocks (
  blocker uuid not null default auth.uid(),
  blocked uuid not null,
  primary key (blocker, blocked)
);

alter table public.community_problems enable row level security;
alter table public.problem_reports    enable row level security;
alter table public.user_blocks        enable row level security;

-- 公開済み（approved）か自分の投稿だけ読める
drop policy if exists "read approved or own" on public.community_problems;
create policy "read approved or own" on public.community_problems
  for select using (status = 'approved' or author = auth.uid());

-- 投稿は必ず pending で、自分名義のみ（status を自分で approved にはできない）
drop policy if exists "insert own pending" on public.community_problems;
create policy "insert own pending" on public.community_problems
  for insert with check (author = auth.uid() and status = 'pending' and review_note is null);

-- 自分の投稿は削除できる（更新は不可。審査結果の書き換えを防ぐ）
drop policy if exists "delete own" on public.community_problems;
create policy "delete own" on public.community_problems
  for delete using (author = auth.uid());

drop policy if exists "report insert" on public.problem_reports;
create policy "report insert" on public.problem_reports
  for insert with check (reporter = auth.uid());

drop policy if exists "block rw" on public.user_blocks;
create policy "block rw" on public.user_blocks
  for all using (blocker = auth.uid()) with check (blocker = auth.uid());

-- 通報が3人以上から来た問題は自動で非公開（flagged）にする
create or replace function public.flag_reported() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from problem_reports where problem_id = new.problem_id) >= 3 then
    update community_problems set status = 'flagged' where id = new.problem_id and status = 'approved';
  end if;
  return new;
end $$;

drop trigger if exists trg_flag_reported on public.problem_reports;
create trigger trg_flag_reported after insert on public.problem_reports
  for each row execute function public.flag_reported();

-- アカウント削除（アプリ内削除の要件）：自分の投稿・通報・ブロックを消す
create or replace function public.delete_my_data() returns void
language sql security definer set search_path = public as $$
  delete from community_problems where author = auth.uid();
  delete from problem_reports where reporter = auth.uid();
  delete from user_blocks where blocker = auth.uid();
$$;

-- ===== コメント機能（問題集） =====
-- problem_key：アプリ内蔵の問題は "b07" のような id、みんなの問題は "c-<uuid>"
create table if not exists public.problem_comments (
  id          uuid primary key default gen_random_uuid(),
  problem_key text not null check (char_length(problem_key) <= 80),
  author      uuid not null default auth.uid(),
  body        text not null check (char_length(body) between 1 and 300),
  hidden      boolean not null default false,   -- 通報が重なると true（本人以外には見えない）
  created_at  timestamptz not null default now()
);
create index if not exists problem_comments_key_idx on public.problem_comments (problem_key, created_at desc);

create table if not exists public.comment_reports (
  id         uuid primary key default gen_random_uuid(),
  comment_id uuid not null references public.problem_comments(id) on delete cascade,
  reporter   uuid not null default auth.uid(),
  reason     text not null check (char_length(reason) <= 300),
  created_at timestamptz not null default now(),
  unique (comment_id, reporter)
);

alter table public.problem_comments enable row level security;
alter table public.comment_reports  enable row level security;

drop policy if exists "comments read" on public.problem_comments;
create policy "comments read" on public.problem_comments
  for select using (hidden = false or author = auth.uid());

drop policy if exists "comments insert" on public.problem_comments;
create policy "comments insert" on public.problem_comments
  for insert with check (author = auth.uid() and hidden = false);

drop policy if exists "comments delete own" on public.problem_comments;
create policy "comments delete own" on public.problem_comments
  for delete using (author = auth.uid());

drop policy if exists "comment report insert" on public.comment_reports;
create policy "comment report insert" on public.comment_reports
  for insert with check (reporter = auth.uid());

create or replace function public.hide_reported_comment() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from comment_reports where comment_id = new.comment_id) >= 3 then
    update problem_comments set hidden = true where id = new.comment_id;
  end if;
  return new;
end $$;

drop trigger if exists trg_hide_reported_comment on public.comment_reports;
create trigger trg_hide_reported_comment after insert on public.comment_reports
  for each row execute function public.hide_reported_comment();

-- アカウント削除に、コメントと通報も含める
create or replace function public.delete_my_data() returns void
language sql security definer set search_path = public as $$
  delete from community_problems where author = auth.uid();
  delete from problem_comments where author = auth.uid();
  delete from comment_reports where reporter = auth.uid();
  delete from problem_reports where reporter = auth.uid();
  delete from user_blocks where blocker = auth.uid();
$$;
