import pytest

from expert_system.services.expert_system import (
    METHOD_BACKWARD,
    METHOD_FORWARD,
    ExpertSystem,
    ExpertSystemError,
)


@pytest.mark.parametrize("method", [METHOD_FORWARD, METHOD_BACKWARD])
def test_objectif_deja_dans_les_faits(kb_exemple, method):
    res = ExpertSystem(kb_exemple).run("cable_branche", method)
    assert res.success
    assert res.rules_applied == ()


def test_objectif_vide_refuse(kb_exemple):
    with pytest.raises(ExpertSystemError):
        ExpertSystem(kb_exemple).run("   ", METHOD_FORWARD)


def test_methode_inconnue_refusee(kb_exemple):
    with pytest.raises(ExpertSystemError):
        ExpertSystem(kb_exemple).run("cable_branche", "zigzag")


def test_choix_du_moteur(kb_exemple):
    es = ExpertSystem(kb_exemple)
    assert es.run("probleme_alimentation", METHOD_FORWARD).method == "chaînage avant"
    assert es.run("probleme_alimentation", METHOD_BACKWARD).method == "chaînage arrière"


def test_is_goal_known(kb_exemple):
    es = ExpertSystem(kb_exemple)
    assert es.is_goal_known(" cable_branche ")
    assert not es.is_goal_known("probleme_alimentation")


def test_changement_d_objectif_est_independant(kb_exemple):
    es = ExpertSystem(kb_exemple)
    es.run("panne_probable_alimentation", METHOD_FORWARD)
    apres = es.run("probleme_alimentation", METHOD_FORWARD)
    frais = ExpertSystem(kb_exemple).run("probleme_alimentation", METHOD_FORWARD)
    assert apres == frais
