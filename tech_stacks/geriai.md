# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GeriApp is a stage-adaptive dementia care platform built with Nuxt 4, Nuxt UI 3, and Supabase. It adapts UI complexity, touch targets, font sizes, and interaction patterns based on a patient's cognitive stage (early/moderate/advanced).

## Commands

```bash
pnpm dev          # Start dev server on http://localhost:3000
pnpm build        # Production build
pnpm preview      # Preview production build locally
pnpm generate     # Static site generation

# Testing (not yet configured — see docs/plans for planned setup)
# pnpm test       # Vitest unit tests
# pnpm lint       # ESLint

# Supabase (requires Supabase CLI + Docker)
supabase start                    # Start local Supabase
supabase migration new <name>     # Create new migration
supabase db push                  # Push migrations to remote
supabase gen types typescript --local > shared/types/database.ts  # Regen DB types
```

## Architecture

**Nuxt 4 directory layout** — `app/` is `srcDir`, `server/` stays at root, `shared/` is for code used by both:

- `app/` — Vue pages, components, composables, layouts, middleware, plugins
- `server/` — Nitro server routes and middleware (deployed as Vercel serverless functions)
- `shared/` — Types and utilities shared between app and server (e.g. `stage-config.ts`, generated DB types)
- `supabase/` — Migrations, Edge Functions, seed data, config

**Key modules:** `@nuxt/ui` (UI components on Reka UI + Tailwind v4), `@nuxtjs/supabase` (auth, sessions, typed client), `@nuxtjs/i18n`, `@pinia/nuxt`, `@vueuse/nuxt`

**Auth:** Handled entirely by `@nuxtjs/supabase` — use `useSupabaseClient()`, `useSupabaseUser()`. No custom auth plugin needed. Route protection via `app/middleware/auth.ts`.

**Stage-adaptive UI:** Core differentiator. `shared/utils/stage-config.ts` defines per-stage configs (touch targets, font sizes, contrast, complexity). `app/composables/useCognitiveStage.ts` provides reactive classes. Stage-aware wrapper components live in `app/components/stage/`.

**Server logic decision:**
- Privileged DB ops, webhooks, exports → `server/api/` (Nuxt server routes with service role key)
- Scheduled jobs, realtime triggers → Supabase Edge Functions + `pg_cron`

**Database:** Postgres via Supabase with RLS. Key tables: `profiles`, `patients`, `patient_assignments`, `care_plans`, `tasks`, `medications`, `medication_logs`, `activities`, `alerts`. Types generated via `supabase gen types`.

**Deployment:** Vercel. Env vars (`NUXT_PUBLIC_SUPABASE_URL`, `NUXT_PUBLIC_SUPABASE_KEY`, `NUXT_SUPABASE_SERVICE_ROLE_KEY`) set in Vercel dashboard.

## Conventions

- Use `~~/shared/` import alias for shared code from within `app/`
- Use `useAsyncData()` for data fetching — Nuxt 4 auto-generates keys from file path + line number
- Use Nuxt UI 3 components (`UButton`, `UCard`, `UForm`, etc.) rather than building custom ones
- Supabase client should be typed: `useSupabaseClient<Database>()`
- Nuxt 4 uses `pages:resolved` hook (not `pages:extend`)
- Migrations are versioned SQL files in `supabase/migrations/` — never use SQL editor directly
- i18n locale files go in `app/locales/` with lazy loading

## Reference

Full technical architecture plan: `docs/plans/geriapp-technical-plan.md`
