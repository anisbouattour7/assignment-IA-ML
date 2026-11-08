from expert_system.engines.backward_chaining import BackwardChaining
from expert_system.engines.forward_chaining import ForwardChaining
from expert_system.models.inference_step import (
    ACTION_CYCLE,
    ACTION_NO_RULE,
    ACTION_RULE_FAILED,
    ACTION_SUBGOAL,
)


def test_objectif_deja_present(kb_exemple):
    res = BackwardChaining().infer(kb_exemple, "cable_branche")
    assert res.success
    assert res.rules_applied == ()


def test_prouve_objectif_avec_chaine_de_regles(kb_exemple):
    res = BackwardChaining().infer(kb_exemple, "panne_probable_alimentation")
    assert res.success
    assert res.rules_applied == ("R1", "R3")
    assert res.derived_facts == ("probleme_alimentation", "panne_probable_alimentation")


def test_condition_non_prouvable(build_kb):
    kb = build_kb(["a"], [("R1", ["a", "b"], "c")])
    res = BackwardChaining().infer(kb, "c")
    assert not res.success
    assert any(s.action == ACTION_RULE_FAILED for s in res.steps)


def test_cycle_sans_recursion_infinie(build_kb):
    kb = build_kb(["x"], [("R1", ["b"], "a"), ("R2", ["a"], "b")])
    res = BackwardChaining().infer(kb, "a")
    assert not res.success
    assert any(s.action == ACTION_CYCLE for s in res.steps)


def test_objectif_sans_fait_ni_regle(kb_exemple):
    res = BackwardChaining().infer(kb_exemple, "inconnu")
    assert not res.success
    assert any(s.action == ACTION_NO_RULE for s in res.steps)


def test_essaie_la_regle_suivante_si_la_premiere_echoue(build_kb):
    kb = build_kb(["b"], [("R1", ["a"], "g"), ("R2", ["b"], "g")])
    res = BackwardChaining().infer(kb, "g")
    assert res.success
    assert res.rules_applied == ("R2",)


def test_faits_initiaux_non_modifies(kb_exemple):
    avant = kb_exemple.fact_names()
    BackwardChaining().infer(kb_exemple, "panne_probable_alimentation")
    assert kb_exemple.fact_names() == avant


def test_trace_arbre_avec_profondeur(kb_exemple):
    res = BackwardChaining().infer(kb_exemple, "panne_probable_alimentation")
    assert [s.number for s in res.steps] == list(range(1, len(res.steps) + 1))
    assert res.steps[0].action == ACTION_SUBGOAL
    assert res.steps[0].depth == 0
    assert max(s.depth for s in res.steps) >= 1


def test_coherence_avec_chainage_avant(kb_exemple):
    """Les deux moteurs doivent conclure pareil pour chaque objectif possible."""
    for goal in [*kb_exemple.known_symbols(), "inconnu"]:
        avant = ForwardChaining().infer(kb_exemple, goal)
        arriere = BackwardChaining().infer(kb_exemple, goal)
        assert avant.success == arriere.success, goal
