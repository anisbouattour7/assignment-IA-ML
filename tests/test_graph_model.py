import pytest

from graph_search.models.graph_model import GraphError, GraphModel


def test_ajout_sommet_unique_et_nettoye():
    g = GraphModel()
    g.add_node("  A  ")
    assert g.nodes() == ["A"]
    with pytest.raises(GraphError):
        g.add_node("A")
    with pytest.raises(GraphError):
        g.add_node("   ")
    with pytest.raises(GraphError):
        g.add_node("B", h=-1)
    assert g.nodes() == ["A"]


def test_arc_oriente_non_symetrique(build_graph):
    g = build_graph(["A", "B"], [("A", "B", 4)])
    assert g.has_edge("A", "B")
    assert not g.has_edge("B", "A")
    assert g.edge_cost("A", "B") == 4


def test_arc_vers_sommet_inexistant_refuse(build_graph):
    g = build_graph(["A"], [])
    with pytest.raises(GraphError):
        g.add_edge("A", "Z", 1)
    with pytest.raises(GraphError):
        g.add_edge("Z", "A", 1)


def test_cout_invalide_refuse(build_graph):
    g = build_graph(["A", "B"], [])
    for bad in (-1, "4", True, None, float("nan"), float("inf")):
        with pytest.raises(GraphError):
            g.add_edge("A", "B", bad)
    assert g.edges() == []


def test_arc_en_double_refuse(build_graph):
    g = build_graph(["A", "B"], [("A", "B", 1)])
    with pytest.raises(GraphError):
        g.add_edge("A", "B", 2)


def test_heuristique(build_graph):
    g = build_graph(["A"], [])
    g.set_heuristic("A", 7)
    assert g.get_heuristic("A") == 7
    g.set_heuristic("A", None)
    assert g.get_heuristic("A") is None
    with pytest.raises(GraphError):
        g.set_heuristic("A", -3)
    with pytest.raises(GraphError):
        g.set_heuristic("Z", 1)


def test_suppression_sommet_retire_ses_arcs(build_graph):
    g = build_graph(["A", "B", "C"], [("A", "B", 1), ("B", "C", 1)])
    g.set_start("B")
    g.remove_node("B")
    assert g.nodes() == ["A", "C"]
    assert g.edges() == []
    assert g.start is None


def test_ordre_des_successeurs_stable(build_graph):
    g = build_graph(["A", "B", "C", "D"], [("A", "C", 1), ("A", "B", 2), ("A", "D", 3)])
    assert g.successors("A") == [("C", 1), ("B", 2), ("D", 3)]


def test_cout_d_un_chemin(graph_exemple):
    assert graph_exemple.path_cost(["A", "B", "G"]) == 16
    assert graph_exemple.path_cost(["A"]) == 0
    with pytest.raises(GraphError):
        graph_exemple.path_cost(["A", "G"])  # cet arc n'existe pas
    with pytest.raises(GraphError):
        graph_exemple.path_cost([])


def test_chargement_graphe_exemple(graph_exemple):
    assert len(graph_exemple.nodes()) == 6
    assert len(graph_exemple.edges()) == 9
    assert graph_exemple.start == "A"
    assert graph_exemple.goal == "G"
    assert graph_exemple.get_heuristic("A") == 7
    assert graph_exemple.get_heuristic("G") == 0


def test_aller_retour_json(graph_exemple, tmp_path):
    out = tmp_path / "graphe.json"
    graph_exemple.save_json(out)
    assert GraphModel.load_json(out).to_dict() == graph_exemple.to_dict()


def test_json_invalide_refuse():
    with pytest.raises(GraphError):
        GraphModel.from_dict(
            {
                "nodes": [{"id": "A"}, {"id": "B"}],
                "edges": [{"source": "A", "target": "B", "cost": "4"}],
            }
        )
    with pytest.raises(GraphError):
        GraphModel.from_dict({"nodes": [{"nom": "A"}]})
    with pytest.raises(GraphError):
        GraphModel.from_dict(["pas", "un", "graphe"])


def test_validation_graphe(graph_exemple):
    assert GraphModel().validate() != []
    assert graph_exemple.validate() == []
