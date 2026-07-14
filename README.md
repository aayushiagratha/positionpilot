# PositionPilot

AI-native GTM and positioning engine that automates ICP creation, messaging frameworks, and GTM strategy generation using specialized multi-agent workflows.

Frontend: [positionpilot-frontend](https://github.com/aayushiagratha/positionpilot-frontend) — live at [positionpilot-ai.vercel.app](https://positionpilot-ai.vercel.app). This repo holds the n8n workflows, schema, and infra the frontend calls into.

> **Scope of this repo:** the 5 user-facing agents of a 14-agent system. The research and governance layer (9 further agents) is not open-sourced.

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

| File | Description |
|------|-------------|
| `PositionPilot - Stage 1.json` | Webhook → Positioning Agent + ICP Agent (parallel) → PostgreSQL |
| `Position Pilot - Stage 2.json` | Webhook → Messaging Agent + GTM Agent (parallel) + Serper → SEO Agent → PostgreSQL → PDF |
| `PositionPilot - Approve Run.json` | Approve webhook → jsonb-merges edited foundation fields into stored output, updates run status to `approved` |

## Database

`schema.sql` defines four tables. Only `strategy_runs` is currently wired into the workflows above — `research_runs`, `competitor_runs`, and `brand_voice_runs` are scaffolded for planned agents (customer research, competitive narrative, brand voice guardrails) that don't exist yet in any workflow file in this repo.

## Setup

1. Install Docker and n8n
2. Create PostgreSQL database, run `schema.sql`
3. Import workflow JSON files into n8n
4. Add credentials:
   - **PostgreSQL** connection
   - **OpenRouter Auth** (Header Auth, header name `Authorization`, value `Bearer <your-openrouter-key>`)
   - **Serper API** (Header Auth, header name `X-API-KEY`, value `<your-serper-key>`) — used by the Stage 2 SEO agent
   - **x-api-key** (Header Auth, header name `x-api-key`, value `<your-generated-secret>`) — required for all three webhooks (Stage 1, Stage 2, Approve Run)
5. On each Webhook trigger node (Stage 1, Stage 2, Approve Run), set **Authentication** to **Header Auth** and select the `x-api-key` credential
6. Activate all 3 workflows
7. Any client calling these webhooks must send the `x-api-key` header on every request, or the call will be rejected with 403

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

All three public webhooks (Stage 1, Stage 2, Approve Run) require a valid `x-api-key` header. Unauthenticated requests are rejected with a 403 before any workflow logic executes.

## Built by

Aayushi Agratha — https://www.linkedin.com/in/aayushiagratha/
