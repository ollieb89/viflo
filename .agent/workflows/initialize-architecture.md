---
description: Initialize the architectural blueprint (PLAN.md) with flexible technology stack and system constraints.
---

# Initialize Architecture Blueprint

This workflow guides the creation of `docs/planning/PLAN.md` with a flexible, user-defined technology stack and constraints.

## Steps

1. **Prompt for Project Goal**
   - Ask the user for the high-level goal of the project (or extract from PRD if available).

2. **Prompt for Technology Stack**
   - Ask the user to specify or confirm the following preferences (defaults in parens):
     - **Frontend Framework** (e.g., Next.js 16, React, Vue)
     - **Backend Language/Framework** (e.g., Node.js/Express, Python/FastAPI, Go)
     - **Database System** (e.g., PostgreSQL, MongoDB, SQLite)
     - **Authentication Provider** (e.g., Clerk, Supabase Auth, NextAuth)
     - **Deployment Target** (e.g., Vercel, Docker/AWS, DigitalOcean)

3. **Prompt for System Constraints**
   - Ask for details on:
     - **Infrastructure Requirements**
     - **Budget / Resource Limits** (Latency targets, Token budgets)
     - **Security Policies** (Auth methods, RLS, Compliance)

4. **Generate Blueprint**
   - Create `docs/planning/PLAN.md` using the collected information.
   - Initial Structure:

     ```markdown
     # Architectural Blueprint

     ## Goal

     [Project Goal]

     ## Tech Stack

     - Frontend: [Frontend Framework]
     - Backend: [Backend Framework]
     - Database: [Database System]
     - Auth: [Authentication Provider]
     - Deployment: [Deployment Target]

     ## System Constraints

     ### Infrastructure

     - Deployment: [Infrastructure Details]
     - Database: [Database Details]

     ### Budget

     - Latency Target: [Latency Target]
     - Token Budget: [Token Budget]

     ### Security

     - Auth: [Auth Strategy]
     - RLS: [Row Level Security Policy]
     ```

5. **Commit Changes**
   - Run: `git add docs/planning/PLAN.md`
   - Run: `git commit -m "docs: initialize PLAN.md with defined architecture"`
