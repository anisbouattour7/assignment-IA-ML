import pytest

from graph_search.algorithms.bfs import BFS
from graph_search.algorithms.dfs import DFS
from graph_search.algorithms.ucs import UCS
from graph_search.models.graph_model import GraphError, GraphModel
from graph_search.models.search_step import ACTION_GOAL, ACTION_INIT, ACTION_STOP, ACTION_UPDATE

ALGOS = [BFS, DFS, UCS]


def test_bfs_minimise_le_nombre_d_arcs(graph_exemple):
    res = BFS().search(graph_exemple, "A", "G")
    assert res.found
    assert res.path == ("A", "B", "G")
    assert res.total_cost == 16  # 2 arcs, mais pas le coût minimal
    assert res.expanded_nodes == ("A", "B", "C", "D", "G")


def test_dfs_descend_en_profondeur(graph_exemple):
    res = DFS().search(graph_exemple, "A", "G")
    assert res.found
    assert res.path == ("A", "B", "D", "G")
    assert res.total_cost == 12
    assert res.expanded_nodes == ("A", "B", "D", "G")


def test_ucs_trouve_le_chemin_de_cout_minimal(graph_exemple):
    res = UCS().search(graph_exemple, "A", "G")
    assert res.found
    assert res.path == ("A", "C", "E", "D", "G")
    assert res.total_cost == 10
    assert res.expanded_nodes == ("A", "C", "B", "E", "D", "G")


def test_ucs_optimal_la_ou_bfs_ne_l_est_pas(build_graph):
    g = build_graph(["S", "M", "G"], [("S", "G", 10), ("S", "M", 1), ("M", "G", 3)])
    assert UCS().search(g, "S", "G").total_cost == 4
    assert BFS().search(g, "S", "G").total_cost == 10


def test_objectif_inaccessible(build_graph):
    g = build_graph(["A", "B", "C"], [("A", "B", 1)])
    for algo in ALGOS:
        res = algo().search(g, "A", "C")
        assert not res.found, algo.code
        assert res.path == ()
        assert res.total_cost is None
        assert "Aucun chemin" in res.message


def test_depart_egal_objectif(graph_exemple):
    for algo in ALGOS:
        res = algo().search(graph_exemple, "A", "A")
        assert res.found, algo.code
        assert res.path == ("A",)
        assert res.total_cost == 0


def test_cycle_sans_boucle_infinie(build_graph):
    g = build_graph(["A", "B", "C"], [("A", "B", 1), ("B", "A", 1), ("A", "A", 1)])
    for algo in ALGOS:
        res = algo().search(g, "A", "C")
        assert not res.found, algo.code


def test_chemin_valide_et_cout_recalcule(graph_exemple):
    for algo in ALGOS:
        res = algo().search(graph_exemple, "A", "G")
        assert res.path[0] == "A" and res.path[-1] == "G", algo.code
        for u, v in zip(res.path, res.path[1:], strict=False):
            assert graph_exemple.has_edge(u, v), algo.code
        assert res.total_cost == graph_exemple.path_cost(res.path), algo.code


def test_depart_ou_objectif_inconnu_refuse(graph_exemple):
    for algo in ALGOS:
        with pytest.raises(GraphError):
            algo().search(graph_exemple, "Z", "G")
        with pytest.raises(GraphError):
            algo().search(graph_exemple, "A", "Z")
        with pytest.raises(GraphError):
            algo().search(GraphModel(), "A", "G")


def test_trace_structuree(graph_exemple, build_graph):
    echec = build_graph(["A", "B"], [])
    for algo in ALGOS:
        res = algo().search(graph_exemple, "A", "G")
        assert [s.index for s in res.steps] == list(range(1, len(res.steps) + 1)), algo.code
        assert res.steps[0].action == ACTION_INIT
        assert res.steps[-1].action == ACTION_GOAL
        assert algo().search(echec, "A", "B").steps[-1].action == ACTION_STOP


def test_ucs_trace_les_mises_a_jour(graph_exemple):
    res = UCS().search(graph_exemple, "A", "G")
    updates = [s for s in res.steps if s.action == ACTION_UPDATE]
    assert updates  # D passe de 10 à 9 puis 7, G de 16 à 12 puis 10
    assert any(s.neighbor == "D" and s.g == 7 for s in updates)


def test_resultats_reproductibles(graph_exemple):
    for algo in ALGOS:
        assert algo().search(graph_exemple, "A", "G") == algo().search(graph_exemple, "A", "G")
