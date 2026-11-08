from expert_system.engines.forward_chaining import ForwardChaining


def test_objectif_deja_present(kb_exemple):
    res = ForwardChaining().infer(kb_exemple, "cable_branche")
    assert res.success
    assert res.rules_applied == ()
    assert res.derived_facts == ()


def test_deduit_objectif_en_plusieurs_regles(kb_exemple):
    res = ForwardChaining().infer(kb_exemple, "panne_probable_alimentation")
    assert res.success
    assert res.derived_facts[-1] == "panne_probable_alimentation"
    assert res.rules_applied.index("R1") < res.rules_applied.index("R3")


def test_arret_des_que_objectif_atteint(kb_exemple):
    res = ForwardChaining().infer(kb_exemple, "probleme_alimentation")
    assert res.success
    assert res.rules_applied == ("R1",)  # R2 n'est pas appliquée inutilement


def test_objectif_non_demontre(build_kb):
    kb = build_kb(["a"], [("R1", ["a", "b"], "c")])
    res = ForwardChaining().infer(kb, "c")
    assert not res.success
    assert res.rules_applied == ()


def test_cycle_de_regles_termine(build_kb):
    kb = build_kb(["a"], [("R1", ["a"], "b"), ("R2", ["b"], "a"), ("R3", ["z"], "goal")])
    res = ForwardChaining().infer(kb, "z")
    assert not res.success
    assert res.rules_applied == ("R1",)


def test_faits_initiaux_non_modifies(kb_exemple):
    avant = kb_exemple.fact_names()
    ForwardChaining().infer(kb_exemple, "panne_probable_alimentation")
    assert kb_exemple.fact_names() == avant


def test_trace_numerotee_et_structuree(kb_exemple):
    res = ForwardChaining().infer(kb_exemple, "panne_probable_alimentation")
    assert [s.number for s in res.steps] == list(range(1, len(res.steps) + 1))
    premiere = res.steps[0]
    assert premiere.rule_id == "R1"
    assert premiere.matched_facts == ("voyant_alimentation_eteint", "cable_branche")
    assert premiere.derived_fact == "probleme_alimentation"
