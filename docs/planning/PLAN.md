# Architectural Blueprint: Universal Agentic Development Environment

## Goal
Maximize velocity while minimizing cost and technical debt via a Hybrid, Planning-First, Agentic methodology.

## Tech Stack
Next.js 16, TypeScript 5.7+, Tailwind v4, Supabase (PostgreSQL), Python FastAPI, PGVector, Vercel/Docker

## System Constraints

### Infrastructure
Infrastructure: Vercel/Supabase; Budget: Latency < 200ms, Cost-Efficient; Security: HttpOnly/JWT, RLS Enabled

### Budget
Infrastructure: Vercel/Supabase; Budget: Latency < 200ms, Cost-Efficient; Security: HttpOnly/JWT, RLS Enabled

### Security
Infrastructure: Vercel/Supabase; Budget: Latency < 200ms, Cost-Efficient; Security: HttpOnly/JWT, RLS Enabled

## Database Schema

### ERD (Mermaid)
See docs/implementation/phase_02.md for ERD

### Schema Definitions (Prisma/SQL)
See docs/implementation/phase_02.md for Schema definitions

## API Surface

### Endpoints
See docs/implementation/phase_02.md for API Surface

## Security & Authorization

### Middleware Strategy
Next.js Middleware for session validation

### RLS Policies
Default deny; specific policies for users/posts
