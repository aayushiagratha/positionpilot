"""Static checks over the exported n8n workflow JSON files and schema.sql.

There's no application code in this repo to unit test — it's n8n workflow
exports plus a Postgres schema. What IS testable and worth guarding: that
every exported workflow is still valid JSON, that the security claim in the
README ("all 10 webhooks sit behind Header Auth") actually holds across every
file, and that the schema defines the tables the workflows/README claim.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_FILES = sorted(ROOT.glob("*.json"))

EXPECTED_TABLES = ["strategy_runs", "research_runs", "competitor_runs", "brand_voice_runs"]


@pytest.fixture(scope="session")
def workflows():
    return {f.name: json.loads(f.read_text(encoding="utf-8")) for f in WORKFLOW_FILES}


def test_found_the_expected_workflow_files():
    # Guards against this test suite silently checking nothing because the
    # glob pattern or working directory is wrong.
    assert len(WORKFLOW_FILES) == 10, f"expected 10 workflow exports, found {len(WORKFLOW_FILES)}"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: p.name)
def test_workflow_file_is_valid_json(path):
    json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: p.name)
def test_workflow_has_n8n_export_shape(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(doc.get("nodes"), list) and doc["nodes"], f"{path.name}: no nodes"
    assert isinstance(doc.get("connections"), dict), f"{path.name}: no connections"


def webhook_trigger_nodes(doc):
    return [n for n in doc["nodes"] if n.get("type") == "n8n-nodes-base.webhook"]


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: p.name)
def test_every_workflow_has_exactly_one_webhook_trigger(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    triggers = webhook_trigger_nodes(doc)
    assert len(triggers) == 1, f"{path.name}: expected 1 webhook trigger, found {len(triggers)}"


@pytest.mark.parametrize("path", WORKFLOW_FILES, ids=lambda p: p.name)
def test_webhook_trigger_requires_header_auth(path):
    """README claims every webhook sits behind Header Auth. Verify it against
    the actual exported node config, not just the docs."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    trigger = webhook_trigger_nodes(doc)[0]
    assert trigger.get("parameters", {}).get("authentication") == "headerAuth", (
        f"{path.name}: webhook trigger is not behind headerAuth"
    )
    assert "httpHeaderAuth" in trigger.get("credentials", {}), (
        f"{path.name}: webhook trigger has no httpHeaderAuth credential attached"
    )


def test_all_webhooks_share_the_same_secret_credential(workflows):
    """A webhook authenticated against a *different* secret than the others
    would silently defeat the "every request needs x-api-key" story."""
    names = set()
    for name, doc in workflows.items():
        trigger = webhook_trigger_nodes(doc)[0]
        names.add(trigger["credentials"]["httpHeaderAuth"]["name"])
    assert names == {"Webhook Secret"}, f"inconsistent webhook credential names: {names}"


def test_schema_defines_all_expected_tables():
    schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
    for table in EXPECTED_TABLES:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in schema, f"schema.sql is missing table {table}"


def test_schema_indexes_generation_run_id_on_every_table():
    """generation_run_id is how a run's rows get correlated back together
    (e.g. audit + rewrite rows in brand_voice_runs) — every table needs an
    index on it or that lookup does a full scan in production."""
    schema = (ROOT / "schema.sql").read_text(encoding="utf-8")
    for table in EXPECTED_TABLES:
        assert f"idx_{table}_generation_run_id" in schema, f"{table} has no generation_run_id index"
