# PositionPilot

AI-native GTM and positioning engine that automates ICP creation, messaging frameworks, and GTM strategy generation using specialized multi-agent workflows.

Frontend: [positionpilot-frontend](https://github.com/aayushiagratha/positionpilot-frontend), deployed on Vercel at [positionpilot-ai.vercel.app](https://positionpilot-ai.vercel.app). This repo holds the n8n workflows, schema, and infra the frontend calls into — n8n currently runs locally via ngrok tunnel, so the deployed frontend isn't always reachable end to end. See the [demo video](https://www.youtube.com/watch?v=R4FTsZzQAOc) for a guaranteed-working walkthrough.

> **Scope of this repo:** all 15 agents across 4 pipelines. The 5 user-facing agents (PositionPilot) are the product; the other 10 — competitive narrative, customer research, and brand voice — are built and published here, but have no frontend calling them yet. See `WORKFLOWS_360.md` for a walkthrough of the three non-PositionPilot layers.

## Demo

[▶ 4-minute product walkthrough](https://www.youtube.com/watch?v=R4FTsZzQAOc) — a live run against a known product (Fathom), the human review/approval step, then the n8n orchestration, model calls, and persistence underneath.

## What it does

PositionPilot takes 9 inputs about a company, drafts a positioning + ICP foundation for human review (edit, add, delete, or AI-rewrite any field), then generates a complete GTM strategy package from the approved foundation:

- Category definition, positioning statement, before/after transformation, memorable hook, brand philosophy, strategic tension, and differentiation pillars
- Ideal Customer Profile (ICP) with primary persona, behavioral signals, buying triggers, and customer fears/risks
- Messaging framework with hero headline, value prop, and messaging pillars
- Go-to-market strategy with distribution channels, launch sequencing, and growth loops
- SEO/AEO strategy with topical authority clusters and high-intent search queries, grounded in real search data

## Architecture

Two-stage pipeline with a human-in-the-loop approval gate:

**Stage 1** — Positioning + ICP agents run in parallel from the same prompt-building step.
**Human gate** — Review and edit Stage 1 output (every field, not just top-level ones) before approving. Approval does a `jsonb` merge (`output || edited_patch`) so edited fields overwrite while everything else the agents produced is preserved.
**Stage 2** — Messaging + GTM agents run in parallel against the approved foundation; Serper (real Google SERP data) runs alongside them and feeds the SEO agent, which runs once that search data is back. All three converge, get persisted, and a PDF is generated.

## Stack

- **Orchestration**: n8n (workflow automation)
- **Database**: PostgreSQL 15
- **Infrastructure**: Docker
- **AI Models**: DeepSeek V4 Flash via OpenRouter
- **SEO Data**: Serper.dev (real Google SERP data)
- **Frontend**: TanStack Start (React), scaffolded via Lovable, deployed on Vercel — see [positionpilot-frontend](https://github.com/aayushiagratha/positionpilot-frontend)

## Workflows

**PositionPilot** — the user-facing product (5 agents):

| File | Description |
|------|-------------|
| `PositionPilot - Stage 1.json` | Webhook → Positioning Agent + ICP Agent (parallel) → PostgreSQL |
| `Position Pilot - Stage 2.json` | Webhook → Messaging Agent + GTM Agent (parallel) + Serper → SEO Agent → PostgreSQL → PDF |
| `PositionPilot - Approve Run.json` | Approve webhook → jsonb-merges edited foundation fields into stored output, updates run status to `approved` |

**Competitive Narrative Mapper** — sourced competitor teardown (4 agents), same Stage 1 → approve → Stage 2 shape:

| File | Description |
|------|-------------|
| `Competitive Narrative Mapper - Stage 1.json` | Webhook → Narrative Agent + Positioning Agent (parallel) → `competitor_runs` |
| `Competitive Narrative Mapper - Stage 2.json` | Webhook → Positioning Opportunity Agent + Differentiation Agent (parallel) → `competitor_runs` |
| `Competitive Narrative Mapper - Approve Run.json` | Approve webhook → merges edits, marks approved |

**CustomerResearch** — pain, triggers, and personas from raw customer data (4 agents):

| File | Description |
|------|-------------|
| `CustomerResearch - Stage 1.json` | Webhook → Pain & Objections Agent + Triggers & Language Agent (parallel) → `research_runs` |
| `CustomerResearch - Stage 2.json` | Webhook → Persona Synthesis Agent + Messaging Intelligence Agent (parallel) → `research_runs` |
| `CustomerResearch - Approve Run.json` | Approve webhook → merges edits, marks approved |

**Brand Voice Guardian** — single-call compliance audit + on-brand rewrite (2 agents). No approve gate:

| File | Description |
|------|-------------|
| `Brand Voice Guardian.json` | Webhook → Compliance Audit Agent + Brand Rewrite Agent (parallel) → `brand_voice_runs` |

A LangGraph port of this one lives in [langgraph-agents](https://github.com/aayushiagratha/langgraph-agents).

## Database

`schema.sql` defines four tables, one per pipeline: `strategy_runs` (PositionPilot), `competitor_runs` (Competitive Narrative Mapper), `research_runs` (CustomerResearch), and `brand_voice_runs` (Brand Voice Guardian). All four are now wired into the workflows above.

## Setup

1. Install Docker and n8n
2. Create PostgreSQL database, run `schema.sql`
3. Import workflow JSON files into n8n
4. Add credentials:
   - **PostgreSQL** connection
   - **OpenRouter Auth** (Header Auth, header name `Authorization`, value `Bearer <your-openrouter-key>`)
   - **Serper API** (Header Auth, header name `X-API-KEY`, value `<your-serper-key>`) — used by the Stage 2 SEO agent
   - **Webhook Secret** (Header Auth, header name `x-api-key`, value `<your-generated-secret>`) — every webhook in every workflow authenticates against this
5. Activate the workflows you need (10 in total; the 3 PositionPilot ones are enough to run the product)
6. Any client calling these webhooks must send the `x-api-key` header on every request, or the call is rejected with 403

## Environment Variables

```
N8N_SECURE_COOKIE=false
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=your-postgres-host
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=postgres
DB_POSTGRESDB_USER=your-user
DB_POSTGRESDB_PASSWORD=your-password
WEBHOOK_URL=your-n8n-url
```

## Security

All 10 webhooks sit behind Header Auth. Every request must carry an `x-api-key` header matching the `Webhook Secret` credential; requests without it are rejected with a 403 before any workflow logic runs. The workflow files carry this setting, so an import brings it with them — you only need to create the credential itself (Setup step 4).

No credentials are committed. Every API key is referenced through an n8n credential (`OpenRouter Auth`, `Serper API`, `pdf`, `Webhook Secret`, the Postgres connection), so the workflow files hold references, never secrets.

## Built by

Aayushi Agratha — https://www.linkedin.com/in/aayushiagratha/

## License

MIT.
