from pathlib import Path

import pytest

from expert_system.models.knowledge_base import KnowledgeBase
from expert_system.models.rule import Rule

EXAMPLE = Path(__file__).parent.parent / "data" / "example_knowledge_base.json"


@pytest.fixture
def kb_exemple() -> KnowledgeBase:
    return KnowledgeBase.load_json(EXAMPLE)


@pytest.fixture
def build_kb():
    """Fabrique une base : build_kb(["a"], [("R1", ["a"], "b")])."""

    def _build(facts, rules):
        kb = KnowledgeBase()
        for f in facts:
            kb.add_fact(f)
        for rule_id, conditions, conclusion in rules:
            kb.add_rule(Rule(rule_id, conditions, conclusion))
        return kb

    return _build
