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

-- ===== 問題ごとの正答率（1回目の解答だけを集計） =====
create table if not exists public.problem_stats (
  problem_key text primary key check (char_length(problem_key) <= 80),
  shown       int not null default 0,
  correct     int not null default 0
);
alter table public.problem_stats enable row level security;

drop policy if exists "stats read" on public.problem_stats;
create policy "stats read" on public.problem_stats for select using (true);
-- 書き込みは下の関数からだけ（直接は書けない）

create or replace function public.record_attempt(p_key text, p_correct boolean) returns void
language sql security definer set search_path = public as $$
  insert into problem_stats (problem_key, shown, correct)
  values (p_key, 1, case when p_correct then 1 else 0 end)
  on conflict (problem_key) do update
    set shown = problem_stats.shown + 1,
        correct = problem_stats.correct + case when p_correct then 1 else 0 end;
$$;
