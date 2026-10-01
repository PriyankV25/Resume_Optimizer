create extension if not exists pgcrypto;

create table if not exists public.resume_configs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade unique,
  resume jsonb not null,
  version integer not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.generated_resumes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  job_description text not null,
  resume jsonb not null,
  ats_score numeric,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.cover_letters (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  job_description text not null,
  resume_id uuid references public.generated_resumes(id) on delete set null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ats_reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  report_type text not null check (report_type in ('original','tailored')),
  resume_id uuid references public.generated_resumes(id) on delete cascade,
  job_description text,
  score numeric not null,
  report jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.generation_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  company text,
  job_title text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists generated_resumes_user_created_idx on public.generated_resumes(user_id, created_at desc);
create index if not exists ats_reports_user_created_idx on public.ats_reports(user_id, created_at desc);
create index if not exists generation_events_user_created_idx on public.generation_events(user_id, created_at desc);

create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists resume_configs_touch on public.resume_configs;
create trigger resume_configs_touch before update on public.resume_configs for each row execute function public.touch_updated_at();
drop trigger if exists generated_resumes_touch on public.generated_resumes;
create trigger generated_resumes_touch before update on public.generated_resumes for each row execute function public.touch_updated_at();
drop trigger if exists cover_letters_touch on public.cover_letters;
create trigger cover_letters_touch before update on public.cover_letters for each row execute function public.touch_updated_at();

alter table public.resume_configs enable row level security;
alter table public.generated_resumes enable row level security;
alter table public.cover_letters enable row level security;
alter table public.ats_reports enable row level security;
alter table public.generation_events enable row level security;

drop policy if exists resume_configs_owner on public.resume_configs;
create policy resume_configs_owner on public.resume_configs for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists generated_resumes_owner on public.generated_resumes;
create policy generated_resumes_owner on public.generated_resumes for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists cover_letters_owner on public.cover_letters;
create policy cover_letters_owner on public.cover_letters for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists ats_reports_owner on public.ats_reports;
create policy ats_reports_owner on public.ats_reports for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists generation_events_owner on public.generation_events;
create policy generation_events_owner on public.generation_events for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

grant select, insert, update, delete on public.resume_configs to authenticated;
grant select, insert, update, delete on public.generated_resumes to authenticated;
grant select, insert, update, delete on public.cover_letters to authenticated;
grant select, insert, update, delete on public.ats_reports to authenticated;
grant select, insert, update, delete on public.generation_events to authenticated;
