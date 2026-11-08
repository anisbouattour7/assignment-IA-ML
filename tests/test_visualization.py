import io

from matplotlib.figure import Figure

from graph_search.algorithms.ucs import UCS
from graph_search.models.graph_model import GraphModel
from ui.visualization import build_figure


def _render(fig) -> None:
    assert isinstance(fig, Figure)
    fig.savefig(io.BytesIO(), format="png")  # force le rendu complet


def test_figure_du_graphe_exemple(graph_exemple):
    _render(build_figure(graph_exemple))


def test_figure_a_chaque_etape_et_chemin_final(graph_exemple):
    res = UCS().search(graph_exemple, "A", "G")
    for step in res.steps:
        _render(build_figure(graph_exemple, step))
    _render(build_figure(graph_exemple, res.steps[-1], res.path))


def test_figure_graphe_vide():
    _render(build_figure(GraphModel()))


def test_figure_avec_cycle_et_boucle(build_graph):
    g = build_graph(["A", "B"], [("A", "B", 1), ("B", "A", 2), ("A", "A", 3)])
    g.set_start("A")
    g.set_goal("B")
    _render(build_figure(g))
