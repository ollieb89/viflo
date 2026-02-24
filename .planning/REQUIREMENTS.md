# Requirements: Viflo v1.3 Expert Skills

**Defined:** 2026-02-24
**Core Value:** A complete agentic dev environment you can install in one command — structured methodology, ready-made skills, and proven workflows so teams skip setup and ship faster.

## v1.3 Requirements

Requirements for v1.3 Expert Skills milestone. Each maps to roadmap phases.

### RAG / Vector Search

- [x] **RAG-01**: User can follow a Quick Start to embed and retrieve documents with pgvector in under 15 minutes
- [x] **RAG-02**: Skill documents chunking strategies (fixed-size vs semantic, overlap rules, token budgets)
- [x] **RAG-03**: Skill includes HNSW index setup and hybrid search with RRF fusion (vector + full-text)
- [x] **RAG-04**: Skill documents 3 named Gotchas with warning signs and fixes (chunking pitfalls, missing HNSW index, embedding model drift)
- [x] **RAG-05**: Skill includes embedding model version column schema and retrieval evaluation patterns (recall@k, MRR)

### Agent Architecture

- [x] **AGENT-01**: User can follow a Quick Start to build a tool-using agent with Anthropic SDK in under 15 minutes
- [x] **AGENT-02**: Skill documents max_turns and max_tokens guardrails as required (not optional), with cost runaway context
- [x] **AGENT-03**: Skill covers streaming output via SSE (FastAPI StreamingResponse) and Vercel AI SDK v6 (Next.js client)
- [x] **AGENT-04**: Skill covers LangGraph stateful multi-agent graphs with v1.1.5 stability note
- [x] **AGENT-05**: Skill covers episodic memory via pgvector (cross-reference to RAG skill) and includes 1-paragraph MCP overview

### Stripe Payments

- [x] **STRIPE-01**: User can follow a Quick Start to accept a one-time payment via Stripe Checkout in under 15 minutes
- [x] **STRIPE-02**: Skill documents webhook handler with raw-body pattern (await req.text()) and atomic idempotency schema
- [x] **STRIPE-03**: Skill covers subscription lifecycle (create, update, cancel, status sync to database)
- [x] **STRIPE-04**: Skill documents 3 named Gotchas with warning signs (raw body destruction, non-atomic idempotency, PCI scope creep)
- [x] **STRIPE-05**: Skill covers Customer Portal integration and trial periods with proration handling

### Infrastructure

- [ ] **INFRA-01**: INDEX.md updated with prompt-engineering v1.2, auth-systems v1.2, and all 3 new/upgraded skills
- [ ] **INFRA-02**: All new/updated SKILL.md files verified ≤500 lines with line counts in VERIFICATION.md
- [ ] **INFRA-03**: Cross-references between RAG ↔ Agent Architecture ↔ prompt-engineering skills added to each skill

## Future Requirements

### Evaluation Architecture

- **EVAL-01**: RAG skill includes golden-set eval.ts with recall@k test cases
- **EVAL-02**: Agent skill includes golden-set eval with tool-call accuracy test cases
- **EVAL-03**: Stripe skill includes golden-set eval with webhook handling test cases

### Advanced Features

- **ADV-01**: Pinecone escape-hatch documentation (>50M vector scale alternative to pgvector)
- **ADV-02**: Multimodal RAG patterns (image embeddings, CLIP)
- **ADV-03**: CrewAI / PydanticAI alternatives to LangGraph documented
- **ADV-04**: Stripe metered billing and usage-based pricing

## Out of Scope

| Feature | Reason |
|---------|--------|
| LangChain deep dives | Blows 500-line budget; framework-agnostic patterns preferred |
| Custom Stripe payment forms | PCI scope increases to SAQ D; hosted Checkout is the right default |
| Multimodal RAG | Storage/complexity cost disproportionate for v1.3 target audience |
| Fine-tuning / model training | Not in viflo scope |
| Eval architecture on new skills | Deferred to future — prompt-engineering already proved the pattern |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| RAG-01 | Phase 12 | Complete |
| RAG-02 | Phase 12 | Complete |
| RAG-03 | Phase 12 | Complete |
| RAG-04 | Phase 12 | Complete |
| RAG-05 | Phase 12 | Complete |
| AGENT-01 | Phase 13 | Complete |
| AGENT-02 | Phase 13 | Complete |
| AGENT-03 | Phase 13 | Complete |
| AGENT-04 | Phase 13 | Complete |
| AGENT-05 | Phase 13 | Complete |
| STRIPE-01 | Phase 14 | Complete |
| STRIPE-02 | Phase 14 | Complete |
| STRIPE-03 | Phase 14 | Complete |
| STRIPE-04 | Phase 14 | Complete |
| STRIPE-05 | Phase 14 | Complete |
| INFRA-01 | Phase 15 | Pending |
| INFRA-02 | Phase 15 | Pending |
| INFRA-03 | Phase 15 | Pending |

**Coverage:**
- v1.3 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-24*
*Last updated: 2026-02-24 after v1.3 roadmap creation (Phases 12–15)*
