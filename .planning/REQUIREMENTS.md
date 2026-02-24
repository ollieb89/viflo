# Requirements: Viflo v1.2 Skills Expansion

**Defined:** 2026-02-24
**Core Value:** A complete agentic dev environment — 35+ skills, GSD methodology, proven workflows, live CI

## v1.2 Requirements

Requirements for the Skills Expansion milestone. Each maps to roadmap phases (Phases 11–14).

### Auth Systems

- [x] **AUTH-01**: Developer can follow a Clerk quick-start to add auth to a Next.js App Router app (sign-up, sign-in, protected routes via proxy.ts)
- [x] **AUTH-02**: Developer can configure Better Auth as the self-hosted alternative with the same protected-route pattern
- [x] **AUTH-03**: Developer can access session data in server components, server actions, and API routes
- [x] **AUTH-04**: Developer can wire OAuth providers (GitHub, Google) through both Clerk and Better Auth
- [x] **AUTH-05**: Skill documents the App Router cache pitfall and DAL re-validation pattern to prevent auth bypass
- [x] **AUTH-06**: Developer can set up a Clerk webhook receiver for user lifecycle sync (created, updated, deleted)

### Stripe Payments

- [ ] **STRIPE-01**: Developer can create a Stripe Checkout session for one-time and subscription payments
- [ ] **STRIPE-02**: Developer can implement an idempotent webhook handler with event.id deduplication and async processing
- [ ] **STRIPE-03**: Developer can set up subscription management and Stripe customer portal
- [ ] **STRIPE-04**: Developer can test webhooks locally using Stripe CLI
- [ ] **STRIPE-05**: Skill documents the Auth→Stripe handoff (signup → Customer → stripe_customer_id → subscription gate)

### RAG / Vector Search

- [ ] **RAG-01**: Developer can implement the full embed → store → query loop using pgvector
- [ ] **RAG-02**: Developer can configure chunking strategy with appropriate chunk size and overlap
- [ ] **RAG-03**: Developer can implement hybrid search (pgvector cosine + PostgreSQL tsvector BM25 + RRF merge)
- [ ] **RAG-04**: Skill documents retrieval evaluation with a golden test set and score-threshold fallback
- [ ] **RAG-05**: Skill enforces the embedding model consistency rule and chunk observability pattern

### Agent Architecture

- [ ] **AGENT-01**: Developer can implement the perceive→reason→act agent loop with Claude API
- [ ] **AGENT-02**: Developer can use the orchestrator–worker pattern for multi-step task decomposition
- [ ] **AGENT-03**: Developer can wire tool/function calling with error handling and partial failure recovery
- [ ] **AGENT-04**: Skill covers memory taxonomy (in-context, external, procedural) with implementation guidance
- [ ] **AGENT-05**: Skill documents token budget awareness and guardrails to prevent runaway agent loops

### Prompt Engineering

- [x] **PROMPT-01**: Developer can write structured prompts using role/context/task/output anatomy
- [x] **PROMPT-02**: Skill documents model-specific technique applicability (instruction-tuned vs reasoning models) with `applies-to:` tags and `last-verified-against:` frontmatter
- [x] **PROMPT-03**: Developer can apply chain-of-thought, few-shot, and output format specification patterns
- [x] **PROMPT-04**: Skill includes an anti-pattern catalogue (top 5 output-degrading patterns)
- [x] **PROMPT-05**: Developer can version and evaluate prompts using a golden set (no external platform required)

### Infrastructure / Compliance

- [ ] **INFRA-01**: INDEX.md updated with new categories (Payments, AI/LLM) and all 5 new skill entries plus Quick Selection Guide entries
- [ ] **INFRA-02**: All 5 new SKILL.md files pass the ≤500 line constraint (CONTENT-01 from v1.1)

## Future Requirements (v1.3+)

### Auth Systems

- **AUTH-F01**: Full RBAC library integration (CASL)
- **AUTH-F02**: SAML/enterprise SSO patterns
- **AUTH-F03**: Multi-tenancy/org management deep dive

### Stripe Payments

- **STRIPE-F01**: Connect/marketplace payments
- **STRIPE-F02**: Invoicing API deep dive
- **STRIPE-F03**: Stripe Tax integration

### RAG / Vector Search

- **RAG-F01**: Multimodal retrieval (images, audio)
- **RAG-F02**: GraphRAG / knowledge graphs
- **RAG-F03**: Fine-tuned embedding models

### Agent Architecture

- **AGENT-F01**: Full LangGraph workflow patterns skill
- **AGENT-F02**: Autonomous agents without human oversight patterns

### Prompt Engineering

- **PROMPT-F01**: Automated evaluation CI pipeline
- **PROMPT-F02**: Red-teaming infrastructure
- **PROMPT-F03**: Multimodal prompting patterns

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auth.js v5 as primary path | Auth.js team moved to Better Auth (Sept 2025); Auth.js is maintenance-mode — cover only as "migrating from" |
| LangGraph full skill | High complexity, separate skill scope; agent-architecture covers concepts, not framework deep-dive |
| Stripe Connect / marketplace | Out of scope for initial payments skill — standard SaaS billing only |
| Automated prompt evaluation CI | Requires platform decisions not yet made; defer to v1.3 |
| Multimodal RAG | Storage and infrastructure complexity; defer to v1.3 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PROMPT-01 | Phase 11 | Complete |
| PROMPT-02 | Phase 11 | Complete |
| PROMPT-03 | Phase 11 | Complete |
| PROMPT-04 | Phase 11 | Complete |
| PROMPT-05 | Phase 11 | Complete |
| AUTH-01 | Phase 11 | Complete |
| AUTH-02 | Phase 11 | Complete |
| AUTH-03 | Phase 11 | Complete |
| AUTH-04 | Phase 11 | Complete |
| AUTH-05 | Phase 11 | Complete |
| AUTH-06 | Phase 11 | Complete |
| RAG-01 | Phase 12 | Pending |
| RAG-02 | Phase 12 | Pending |
| RAG-03 | Phase 12 | Pending |
| RAG-04 | Phase 12 | Pending |
| RAG-05 | Phase 12 | Pending |
| AGENT-01 | Phase 12 | Pending |
| AGENT-02 | Phase 12 | Pending |
| AGENT-03 | Phase 12 | Pending |
| AGENT-04 | Phase 12 | Pending |
| AGENT-05 | Phase 12 | Pending |
| STRIPE-01 | Phase 13 | Pending |
| STRIPE-02 | Phase 13 | Pending |
| STRIPE-03 | Phase 13 | Pending |
| STRIPE-04 | Phase 13 | Pending |
| STRIPE-05 | Phase 13 | Pending |
| INFRA-01 | Phase 14 | Pending |
| INFRA-02 | Phase 14 | Pending |

**Coverage:**
- v1.2 requirements: 27 total
- Mapped to phases: 27
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-24*
*Last updated: 2026-02-24 — roadmap created (Phases 11–14)*
