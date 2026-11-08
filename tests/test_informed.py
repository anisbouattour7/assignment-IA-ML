import pytest

from graph_search.algorithms.astar import AStar
from graph_search.algorithms.bfs import BFS
from graph_search.algorithms.greedy import GreedyBestFirst
from graph_search.algorithms.ucs import UCS
from graph_search.models.graph_model import GraphError, GraphModel
from graph_search.models.search_step import ACTION_EXPAND, ACTION_UPDATE

INFORMED = [GreedyBestFirst, AStar]


def _graphe_piege(h_b: float = 1) -> GraphModel:
    """S→A (1), S→B (5), A→G (100), B→G (1) : A paraît proche mais mène à un chemin coûteux."""
    g = GraphModel()
    for node in "SABG":
        g.add_node(node)
    g.add_edge("S", "A", 1)
    g.add_edge("S", "B", 5)
    g.add_edge("A", "G", 100)
    g.add_edge("B", "G", 1)
    for node, h in {"S": 3, "A": 1, "B": h_b, "G": 0}.items():
        g.set_heuristic(node, h)
    return g


def test_gloutonne_sur_le_graphe_exemple(graph_exemple):
    res = GreedyBestFirst().search(graph_exemple, "A", "G")
    assert res.found
    assert res.path == ("A", "B", "G")
    assert res.total_cost == 16  # pas optimal : le coût parcouru est ignoré
    assert res.expanded_nodes == ("A", "B", "G")


def test_astar_optimal_sur_le_graphe_exemple(graph_exemple):
    res = AStar().search(graph_exemple, "A", "G")
    assert res.path == ("A", "C", "E", "D", "G")
    assert res.total_cost == 10
    assert res.expanded_nodes == ("A", "C", "B", "E", "D", "G")
    assert res.warnings == ()  # h est admissible


def test_gloutonne_trompee_par_l_heuristique():
    g = _graphe_piege()
    greedy = GreedyBestFirst().search(g, "S", "G")
    assert greedy.path == ("S", "A", "G")
    assert greedy.total_cost == 101
    assert UCS().search(g, "S", "G").total_cost == 6
    assert greedy.warnings  # non-optimalité signalée


def test_astar_optimal_avec_heuristique_admissible():
    res = AStar().search(_graphe_piege(), "S", "G")
    assert res.path == ("S", "B", "G")
    assert res.total_cost == 6
    assert res.warnings == ()


def test_astar_rouvre_un_sommet_si_h_est_incoherente(build_graph):
    g = build_graph(
        ["S", "A", "B", "G"],
        [("S", "A", 3), ("S", "B", 1), ("B", "A", 1), ("A", "G", 5)],
    )
    for node, h in {"S": 0, "A": 0, "B": 5, "G": 0}.items():
        g.set_heuristic(node, h)  # admissible mais incohérente (h(B) > 1 + h(A))
    res = AStar().search(g, "S", "G")
    assert res.path == ("S", "B", "A", "G")
    assert res.total_cost == 7
    assert res.expanded_nodes == ("S", "A", "B", "A", "G")  # A est développé deux fois
    assert any(s.action == ACTION_UPDATE and "Réouverture" in s.explanation for s in res.steps)


def test_heuristique_manquante_bloque_la_recherche(build_graph):
    g = build_graph(["A", "B", "G"], [("A", "B", 1), ("B", "G", 1)])
    for algo in INFORMED:
        with pytest.raises(GraphError, match="manquante"):
            algo().search(g, "A", "G")
    assert BFS().search(g, "A", "G").found  # la recherche non informée n'en a pas besoin


def test_heuristique_invalide_bloque_la_recherche(graph_exemple):
    mauvais = {"A": 7, "B": -1, "C": 5, "D": 2, "E": 4, "G": 0}
    for algo in INFORMED:
        with pytest.raises(GraphError, match="invalide"):
            algo().search(graph_exemple, "A", "G", heuristic=mauvais)


def test_heuristique_de_l_objectif_vaut_zero_par_defaut(build_graph):
    g = build_graph(["A", "B", "G"], [("A", "B", 1), ("B", "G", 1)])
    g.set_heuristic("A", 2)
    g.set_heuristic("B", 1)  # pas de h pour G
    for algo in INFORMED:
        res = algo().search(g, "A", "G")
        assert res.path == ("A", "B", "G"), algo.code


def test_astar_avertit_si_h_n_est_pas_admissible():
    res = AStar().search(_graphe_piege(h_b=2), "S", "G")  # h(B)=2 > coût réel 1
    assert res.warnings
    assert "h(B)" in res.warnings[0]


def test_depart_egal_objectif_informees(build_graph):
    g = build_graph(["A"], [])
    for algo in INFORMED:
        res = algo().search(g, "A", "A")
        assert res.path == ("A",), algo.code
        assert res.total_cost == 0


def test_objectif_inaccessible_informees(build_graph):
    g = build_graph(["A", "B", "C"], [("A", "B", 1)])
    g.set_heuristic("A", 1)
    g.set_heuristic("B", 1)  # C est inaccessible : pas besoin de h pour lui
    for algo in INFORMED:
        res = algo().search(g, "A", "C")
        assert not res.found, algo.code
        assert res.total_cost is None


def test_cycle_sans_boucle_infinie_informees(build_graph):
    g = build_graph(["A", "B", "C"], [("A", "B", 1), ("B", "A", 1)])
    g.set_heuristic("A", 1)
    g.set_heuristic("B", 1)
    for algo in INFORMED:
        assert not algo().search(g, "A", "C").found, algo.code


def test_chemin_valide_et_cout_recalcule_informees(graph_exemple):
    for algo in INFORMED:
        res = algo().search(graph_exemple, "A", "G")
        for u, v in zip(res.path, res.path[1:], strict=False):
            assert graph_exemple.has_edge(u, v), algo.code
        assert res.total_cost == graph_exemple.path_cost(res.path), algo.code


def test_trace_informee(graph_exemple):
    for algo in INFORMED:
        res = algo().search(graph_exemple, "A", "G")
        assert [s.index for s in res.steps] == list(range(1, len(res.steps) + 1))
        expands = [s for s in res.steps if s.action == ACTION_EXPAND]
        assert expands and all(s.h is not None for s in expands), algo.code
    for step in AStar().search(graph_exemple, "A", "G").steps:
        if step.action == ACTION_EXPAND:
            assert step.f == step.g + step.h
