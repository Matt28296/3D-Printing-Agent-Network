"""Every agent and skill file must have frontmatter Claude Code can parse."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
AGENTS = sorted((ROOT / ".claude" / "agents").glob("*.md"))
SKILLS = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md"))
AGENT_KEYS = {"name", "description", "tools", "model", "effort", "skills", "color"}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), path
    return yaml.safe_load(text[4:].partition("\n---\n")[0])


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_frontmatter(path):
    fm = frontmatter(path)
    assert fm["name"] == path.stem and fm["description"]
    assert set(fm) <= AGENT_KEYS, set(fm) - AGENT_KEYS
    assert fm["model"] in {"opus", "sonnet", "haiku", "inherit"}
    for skill in fm.get("skills", []):
        assert (ROOT / ".claude" / "skills" / skill / "SKILL.md").exists(), skill


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_skill_frontmatter(path):
    fm = frontmatter(path)
    assert fm["name"] == path.parent.name and fm["description"]


def test_agents_only_reference_existing_agents():
    names = {p.stem for p in AGENTS}
    for p in AGENTS:
        text = p.read_text()
        for word in ("lead", "engineer", "reviewer", "analyst", "auditor", "operator", "tech", "orchestrator"):
            for token in {t.strip("`*.,:;()") for t in text.split() if t.strip("`*.,:;()").endswith("-" + word)}:
                assert token in names, f"{p.name} mentions unknown agent {token}"
