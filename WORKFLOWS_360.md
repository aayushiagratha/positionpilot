# The Other Workflows — 360° View

Compiled 2026-07-07 by directly opening each workflow in the live n8n instance (`localhost:5678`). These three layers exist and are **Published** in n8n, are now **exported to this repo** (see update below), but remain **not called by the frontend** and have **no verified end-to-end test run** (unlike the main PositionPilot pipeline, which was verified live multiple times this project). Treat anything not explicitly marked "verified" as inferred from workflow structure, not confirmed by execution.

> **Update 2026-07-17 —** all three layers are now exported to this repo; findings 1 and 4 below reflect that. The rest of this snapshot still reads as compiled on 2026-07-07.

## Why these weren't in this repo *(resolved 2026-07-17)*

Originally only `PositionPilot - Stage 1`, `Position Pilot - Stage 2`, and `PositionPilot - Approve Run` were exported here — the three layers below were built directly in the n8n editor and never exported, so losing the n8n instance/Docker volume would have lost the work.

All seven are now exported to this repo, alongside fresh re-exports of the original three. The two `_temp_*` utility workflows were deliberately excluded as scratch.

## Inventory

| Workflow (n8n name) | Status | Maps to schema table |
|---|---|---|
| Brand Voice Guardian | Published | `brand_voice_runs` |
| Competitive Narrative Mapper - Stage 1 | Published | `competitor_runs` |
| Competitive Narrative Mapper - Approve Run | Published | `competitor_runs` |
| Competitive Narrative Mapper - Stage 2 | Published | `competitor_runs` |
| CustomerResearch - Stage 1 | Published | `research_runs` |
| CustomerResearch - Approve Run | Published | `research_runs` |
| CustomerResearch - Stage 2 | Published | `research_runs` |
| _temp_pdf_data_export | Published | n/a (utility) |
| _temp_create_research_table | Published | n/a (utility, one-off table creation) |

**Not opened / not verified in this pass:** Competitive Narrative Mapper - Approve Run, Competitive Narrative Mapper - Stage 2, CustomerResearch - Approve Run, CustomerResearch - Stage 2, both `_temp_*` utility workflows, and the exact prompt for "Triggers & Language Agent" (only its input shape was inferred from context, not read directly).

---

## 1. Brand Voice Guardian

**Shape:** single webhook workflow (not split into Stage 1/2 like the others) — takes any piece of content plus brand guidelines, returns a compliance audit and an on-brand rewrite in one call.

**Flow:** Webhook → `Is Valid?` → **Compliance Audit Agent** + **Brand Rewrite Agent** (parallel) → JSON gates → Merge Results → Reshape Data → Persist Results (Postgres) → Respond. Has its own `Error Response` and `Catch Response` error-handling paths.

**Input (inferred from prompt template):** `brand_voice_guidelines` (text), `content_type` (optional, defaults to `'general'`), `content_to_review` (the actual copy to check).

**Compliance Audit Agent** — verified prompt:
- System role: "brand voice compliance auditor"
- Returns: `compliance_score` (0-100), `grade` (A-F style), `summary`, `violations[]` (each with `violation_id`, `severity`: critical/major/minor, `original_text`, `issue`, `guideline_reference`, `confidence_score`), `strengths[]`, `tone_analysis` (`detected_tones[]`, `required_tones[]`, `alignment_score`), `word_pattern_flags[]` (jargon/filler/off-brand words)

**Brand Rewrite Agent** — verified prompt, runs independently in parallel (not gated behind the audit result):
- System role: "brand voice copywriter"
- Returns: `rewritten_content` (full on-brand rewrite), `changes_made[]` (each with `violation_id`, `original`, `rewritten`, `rationale`), `rewrite_confidence`, `notes`

**Model:** `deepseek/deepseek-v4-flash` for both agents (audit at temperature 0.1, rewrite at 0.3 — slightly more creative for the rewrite, sensible choice).

**Practical fit:** this is the most immediately reusable of the three — it could run against PositionPilot's own generated Messaging output as an optional "brand consistency" pass, without needing any data the user doesn't already have.

---

## 2. Competitive Narrative Mapper

**Shape:** mirrors the main pipeline exactly — Stage 1 (parallel agents) → human Approve gate → Stage 2. Only Stage 1 was opened in this pass.

**Stage 1 flow:** Webhook → `Is Valid?` → **Narrative Agent** + **Positioning Agent** (parallel, both fed from a "Market Context Contextualizer" pre-processing step) → JSON gates → Merge Research → Reshape Data → Persist Stage 1 (Postgres, table `competitor_runs`) → Respond.

**Narrative Agent** — verified prompt:
- System role: "brand narrative and messaging analyst" — for each competitor, extracts narrative/messaging intelligence
- Returns per competitor: `messaging_pillars[]`, `pain_points_addressed[]`, `proof_points[]` (social proof/awards), `tone_of_voice[]`, `cta_style`, `emotional_hook`, plus `confidence_scores` per field
- Input: `company_name`, `product_context`, `industry` (+ a competitor list, not fully traced)

**"Positioning Agent"** (misleading name — this is a competitive-intelligence agent, distinct from the main pipeline's Positioning Agent) — verified prompt:
- System role: "competitive intelligence analyst" — for each competitor, extracts positioning data
- Returns per competitor: `threat_tier` (primary/secondary/peripheral), `headline`, `tagline`, `core_value_prop`, `target_audience[]`, `differentiators[]`, market/premium positioning, **`sources[]`** (`source_url` + `extracted_claim` per source — i.e., grounded, cited claims, not the model's guess)

**Model:** `deepseek/deepseek-v4-flash`, temperature 0.2 for both.

**Why this one matters most:** the main PositionPilot pipeline's Positioning Agent only ever sees the user's own free-text guess at who their competitors are (`primary_competitors` field) — it does no actual research. This layer does real, sourced competitor teardown. It's the single highest-leverage piece of unused work here if the goal is to make PositionPilot's differentiation claims more credible.

**Not verified:** Stage 2's agents, the Approve Run merge logic, and whether the citation URLs are backed by a live search call (Serper) or are model-generated guesses at plausible URLs — this matters a lot for whether "sourced" claims are actually trustworthy, and should be checked before relying on this output for anything customer-facing.

---

## 3. CustomerResearch

**Shape:** also mirrors the main pipeline — Stage 1 → Approve → Stage 2. Only Stage 1 was opened.

**Stage 1 flow:** Webhook → `Is Valid?` → **Pain & Objections Agent** + **Triggers & Language Agent** (parallel) → JSON gates → Merge Research → Reshape Data → Persist Research (Postgres, confirmed query: `INSERT INTO research_runs (...) VALUES (..., 'pain', ...), (..., 'triggers', ...)`) → Respond.

**Pain & Objections Agent** — verified prompt:
- System role: "expert customer research analyst specialising in B2B SaaS"
- Instructed to analyze **raw customer data** (not a form field — an actual text blob: reviews, support tickets, call transcripts) and extract structured pain/objection insights, explicitly told to use the customer's own words and avoid generic summaries
- Input: `company_name`, `data_type` (defaults to `'mixed customer data'`), `product_context` (defaults to `'B2B SaaS product'`), `raw_data` (the actual blob)

**Triggers & Language Agent** — not opened directly; inferred from workflow position (parallel to Pain & Objections, same input shape) to extract buying triggers and exact customer vocabulary/phrasing from the same raw data.

**Model:** `deepseek/deepseek-v4-flash`, temperature 0.2.

**The catch:** this agent is only as good as the raw customer data you feed it. PositionPilot's actual target user (early-stage founder, per the product's own positioning) usually doesn't have a corpus of reviews or support tickets yet. Well-built agent, questionable fit to the current product's cold-start reality — worth deciding who would actually use this before investing more in it.

---

## Cross-cutting findings (apply to all three layers)

1. **Credential handling — consistent across all layers.** Every OpenRouter HTTP node in these three layers authenticates through n8n's stored credential store (`genericCredentialType` / `httpHeaderAuth`, via the shared "OpenRouter Auth" credential), matching the main PositionPilot pipeline. `HTTP-Referer` and `X-Title` remain plain headers. No credentials are held in the workflow definitions, so these exports are safe to publish.

2. **No frontend exists for any of these.** Even though Competitive Narrative Mapper and CustomerResearch both have an Approve Run workflow (implying a designed human-review gate, same pattern as the main pipeline), there is no UI anywhere that calls these webhooks, displays their draft output for review, or lets a user approve them. Backend-complete, frontend-absent.

3. **No confirmed end-to-end test.** Unlike the main pipeline (personally verified this session with real generated data across multiple runs), none of these three layers were run with real input during this investigation. Before trusting any claim that they're "tested and working," check the actual row counts and contents in `research_runs`, `competitor_runs`, and `brand_voice_runs` directly.

4. ~~**Not exported to this repo.**~~ **Fixed 2026-07-17.** All three layers are now exported here (7 files), so they no longer exist only in the live n8n instance. The exports were pulled via `n8n export:workflow` run inside the `positionpilot-n8n` container — note the instance is backed by the `positionpilot-postgres` container, *not* the `~/.n8n` SQLite file, which is empty and misleading.

---

*Compiled by direct inspection on 2026-07-07. Like `PROJECT_360.md`, this is a snapshot — it will go stale as these workflows change, and several sub-parts (Stage 2 of two layers, both Approve Run workflows, the two `_temp_*` utilities) were not opened in this pass.*
