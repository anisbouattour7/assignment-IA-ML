from pathlib import Path

import pytest

from expert_system.models.knowledge_base import KnowledgeBase, KnowledgeBaseError
from expert_system.models.rule import Rule

EXAMPLE = Path(__file__).parent.parent / "data" / "example_knowledge_base.json"


def test_ajout_fait_sans_doublon():
    kb = KnowledgeBase()
    assert kb.add_fact("a") is True
    assert kb.add_fact("a") is False
    assert kb.fact_names() == {"a"}


def test_fait_vide_refuse():
    with pytest.raises(ValueError):
        KnowledgeBase().add_fact("   ")


def test_suppression_fait_inconnu():
    with pytest.raises(KnowledgeBaseError):
        KnowledgeBase().remove_fact("zzz")


def test_ajout_et_suppression_regle():
    kb = KnowledgeBase()
    kb.add_rule(Rule("R1", ["a"], "b"))
    assert [r.id for r in kb.get_rules()] == ["R1"]
    kb.remove_rule("R1")
    assert kb.get_rules() == []


def test_regle_id_duplique_refusee():
    kb = KnowledgeBase()
    kb.add_rule(Rule("R1", ["a"], "b"))
    with pytest.raises(KnowledgeBaseError):
        kb.add_rule(Rule("R1", ["c"], "d"))


def test_regle_sans_condition_ou_sans_conclusion_refusee():
    with pytest.raises(KnowledgeBaseError):
        KnowledgeBase().add_rule(Rule("R1", [], "b"))
    with pytest.raises(KnowledgeBaseError):
        KnowledgeBase().add_rule(Rule("R1", ["a"], ""))


def test_chargement_exemple_et_symboles():
    kb = KnowledgeBase.load_json(EXAMPLE)
    assert len(kb.get_facts()) == 3
    assert len(kb.get_rules()) == 3
    assert "verifier_bloc_alimentation" in kb.known_symbols()
    assert kb.validate() == []


def test_aller_retour_json(tmp_path):
    kb = KnowledgeBase.load_json(EXAMPLE)
    out = tmp_path / "kb.json"
    kb.save_json(out)
    assert KnowledgeBase.load_json(out).to_dict() == kb.to_dict()


def test_modification_fait_conserve_l_ordre():
    kb = KnowledgeBase()
    for f in ("a", "b", "c"):
        kb.add_fact(f)
    kb.update_fact("b", "  x ")
    assert [f.name for f in kb.get_facts()] == ["a", "x", "c"]


def test_modification_fait_doublon_refuse():
    kb = KnowledgeBase()
    kb.add_fact("a")
    kb.add_fact("b")
    with pytest.raises(KnowledgeBaseError):
        kb.update_fact("a", "b")


def test_modification_regle():
    kb = KnowledgeBase()
    kb.add_rule(Rule("R1", ["a"], "b"))
    kb.add_rule(Rule("R2", ["b"], "c"))
    kb.update_rule("R1", Rule("R1x", ["a", "z"], "b"))
    assert [r.id for r in kb.get_rules()] == ["R1x", "R2"]
    assert kb.get_rules()[0].conditions == ("a", "z")


def test_modification_regle_id_duplique_refuse():
    kb = KnowledgeBase()
    kb.add_rule(Rule("R1", ["a"], "b"))
    kb.add_rule(Rule("R2", ["b"], "c"))
    with pytest.raises(KnowledgeBaseError):
        kb.update_rule("R1", Rule("R2", ["a"], "b"))


def test_modification_regle_inconnue_ou_invalide():
    kb = KnowledgeBase()
    kb.add_rule(Rule("R1", ["a"], "b"))
    with pytest.raises(KnowledgeBaseError):
        kb.update_rule("R9", Rule("R9", ["a"], "b"))
    with pytest.raises(KnowledgeBaseError):
        kb.update_rule("R1", Rule("R1", [], "b"))
