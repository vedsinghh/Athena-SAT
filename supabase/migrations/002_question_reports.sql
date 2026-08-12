-- Athena SAT: question issue reports from practice sessions
-- Run in Supabase → SQL Editor after 001_profiles.sql

create extension if not exists pgcrypto;

create table if not exists public.question_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users (id) on delete set null,
  user_email text,
  profile_name text,
  subject text not null check (subject in ('math', 'reading')),
  question_id text not null,
  question_pool text,
  question_domain text,
  question_skill text,
  question_difficulty text,
  question_prompt text,
  reason text not null,
  details text,
  page_url text,
  created_at timestamptz not null default now()
);

create index if not exists question_reports_created_at_idx
  on public.question_reports (created_at desc);

create index if not exists question_reports_question_id_idx
  on public.question_reports (question_id);

alter table public.question_reports enable row level security;

-- Any signed-in user can submit a report
drop policy if exists "question_reports_insert_own" on public.question_reports;
create policy "question_reports_insert_own"
  on public.question_reports for insert
  to authenticated
  with check (auth.uid() = user_id);

-- Users can read their own submissions
drop policy if exists "question_reports_select_own" on public.question_reports;
create policy "question_reports_select_own"
  on public.question_reports for select
  to authenticated
  using (auth.uid() = user_id);

-- Inbox for site owners (edit emails as needed)
drop policy if exists "question_reports_admin_select" on public.question_reports;
create policy "question_reports_admin_select"
  on public.question_reports for select
  to authenticated
  using (
    lower(coalesce(auth.jwt() ->> 'email', '')) in (
      'support@athenasat.app',
      'vedsingh1208@gmail.com'
    )
  );

grant usage on schema public to authenticated;
grant select, insert on table public.question_reports to authenticated;
