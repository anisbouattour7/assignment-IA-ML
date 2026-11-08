import pytest

from graph_search.algorithms.base import CATEGORY_INFORMED, CATEGORY_UNINFORMED
from graph_search.algorithms.registry import ALGORITHMS, algorithms_in
from graph_search.models.graph_model import GraphError, GraphModel
from graph_search.models.search_config import SearchConfig
from graph_search.services.search_service import SearchService


def test_service_lance_les_cinq_algorithmes(graph_exemple):
    service = SearchService()
    for code in ALGORITHMS:
        res = service.run(graph_exemple, SearchConfig("A", "G", code))
        assert res.found, code
        assert res.algorithm == code


def test_service_refuse_un_algorithme_inconnu(graph_exemple):
    with pytest.raises(GraphError, match="inconnu"):
        SearchService().run(graph_exemple, SearchConfig("A", "G", "IDS"))


def test_service_refuse_une_categorie_incoherente(graph_exemple):
    config = SearchConfig("A", "G", "BFS", category=CATEGORY_INFORMED)
    with pytest.raises(GraphError, match="catégorie"):
        SearchService().run(graph_exemple, config)


def test_service_bloque_l_informee_sans_heuristique(build_graph):
    g = build_graph(["A", "B", "G"], [("A", "B", 1), ("B", "G", 1)])
    service = SearchService()
    with pytest.raises(GraphError, match="manquante"):
        service.run(g, SearchConfig("A", "G", "A*"))
    assert service.run(g, SearchConfig("A", "G", "BFS")).found


def test_service_valide_sans_lever_d_exception(graph_exemple):
    service = SearchService()
    assert service.validate(graph_exemple, SearchConfig("A", "G", "A*")) == []
    assert service.validate(graph_exemple, SearchConfig("Z", "G", "BFS")) != []
    assert service.validate(GraphModel(), SearchConfig("A", "G", "BFS")) != []


def test_service_utilise_l_heuristique_fournie(graph_exemple):
    h = {"A": 7, "B": 5, "C": 1, "D": 2, "E": 4, "G": 0}
    res = SearchService().run(graph_exemple, SearchConfig("A", "G", "Gloutonne"), heuristic=h)
    assert res.path == ("A", "C", "D", "G")
    assert res.total_cost == 13


def test_registre_des_algorithmes_par_categorie():
    assert [a.code for a in algorithms_in(CATEGORY_UNINFORMED)] == ["BFS", "DFS", "UCS"]
    assert [a.code for a in algorithms_in(CATEGORY_INFORMED)] == ["Gloutonne", "A*"]
