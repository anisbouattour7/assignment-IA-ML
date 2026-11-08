from expert_system.models.rule import Rule


def test_applicable_si_toutes_les_conditions_presentes():
    assert Rule("R1", ["a", "b"], "c").is_applicable({"a", "b", "x"})


def test_non_applicable_si_une_condition_manque():
    assert not Rule("R1", ["a", "b"], "c").is_applicable({"a"})


def test_regle_sans_condition_jamais_applicable():
    assert not Rule("R1", [], "c").is_applicable({"a"})


def test_affichage_si_alors():
    assert str(Rule("R1", ["a", "b"], "c")) == "R1 : SI a ET b ALORS c"
