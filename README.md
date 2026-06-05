# PositionPilot

AI-native GTM and positioning engine that automates ICP creation, messaging frameworks, and GTM strategy generation using specialized multi-agent workflows.

## What it does

PositionPilot takes 8 inputs about a company and produces a complete GTM strategy package including:

- Positioning statement and category definition
- Ideal Customer Profile (ICP) with buying triggers and economic buyer profile
- Messaging framework with hero headline, value prop, and messaging pillars
- Go-to-market strategy with distribution channels, launch sequencing, and growth loops
- SEO/AEO strategy with topical authority clusters and high-intent search queries

## Architecture

Two-stage pipeline with human-in-the-loop approval gate:

**Stage 1** — Positioning + ICP agents run in parallel  
**Human gate** — Review and approve Stage 1 output before Stage 2 runs  
**Stage 2** — Messaging + GTM + SEO agents run in parallel

## Stack

- **Orchestration**: n8n (workflow automation)
- **Database**: PostgreSQL 15
- **Infrastructure**: Docker
- **AI Models**: DeepSeek V4 Flash/Pro via OpenRouter
- **SEO Data**: Serper.dev (real Google SERP data)
- **Frontend**: Lovable

## Workflows

| File | Description |
|------|-------------|
| `PositionPilot - Stage 1.json` | Webhook → Positioning Agent + ICP Agent → PostgreSQL |
| `Position Pilot - Stage 2.json` | Webhook → Messaging Agent + GTM Agent + SEO Agent → PostgreSQL |
| `PositionPilot - Approve Run.json` | Approve webhook → updates run status to approved |

## Setup

1. Install Docker and n8n
2. Create PostgreSQL database
3. Import workflow JSON files into n8n
4. Add credentials: OpenRouter API key (Header Auth) + PostgreSQL connection
5. Activate all 3 workflows

## Environment Variables
N8N_SECURE_COOKIE=false
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=your-postgres-host
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=postgres
DB_POSTGRESDB_USER=your-user
DB_POSTGRESDB_PASSWORD=your-password
WEBHOOK_URL=your-n8n-url

## Output Quality

Tested on: PositionPilot, Notion, Gravity, Antimattr, Alphatech  
Average output rating: 9/10

## Built by

Aayushi Agratha — [LinkedIn] - https://www.linkedin.com/in/aayushiagratha/
