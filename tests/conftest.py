from pathlib import Path

import pytest

from expert_system.models.knowledge_base import KnowledgeBase
from expert_system.models.rule import Rule
from graph_search.models.graph_model import GraphModel

EXAMPLE = Path(__file__).parent.parent / "data" / "example_knowledge_base.json"
SAMPLE_GRAPH = Path(__file__).parent.parent / "data" / "sample_graph.json"


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


@pytest.fixture
def graph_exemple() -> GraphModel:
    return GraphModel.load_json(SAMPLE_GRAPH)


@pytest.fixture
def build_graph():
    """Fabrique un graphe : build_graph(["A", "B"], [("A", "B", 4)])."""

    def _build(nodes, edges):
        graph = GraphModel()
        for node in nodes:
            graph.add_node(node)
        for source, target, cost in edges:
            graph.add_edge(source, target, cost)
        return graph

    return _build
