import networkx as nx
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from graph_search.algorithms.base import fmt
from graph_search.models.graph_model import GraphModel
from graph_search.models.search_step import SearchStep

COLOR_DEFAULT = "#E5E7EB"
COLOR_VISITED = "#93C5FD"
COLOR_FRONTIER = "#FDE68A"
COLOR_CURRENT = "#FB923C"
COLOR_PATH = "#86EFAC"
BORDER_START = "#16A34A"
BORDER_GOAL = "#DC2626"
BORDER_DEFAULT = "#374151"
NODE_SIZE = 900
CURVE = "arc3,rad=0.12"  # courbe légère : deux arcs opposés A→B et B→A restent lisibles


def build_figure(
    graph: GraphModel,
    step: SearchStep | None = None,
    path: tuple[str, ...] = (),
) -> Figure:
    """Dessine le graphe. Sans étape : aperçu. Avec une étape : sommet courant, frontière,
    sommets développés et arc examiné. Avec `path` : chemin final en vert."""
    fig = Figure(figsize=(7, 5))
    ax = fig.subplots()
    ax.axis("off")
    g = graph.graph
    if g.number_of_nodes() == 0:
        ax.text(0.5, 0.5, "Graphe vide : ajoutez des sommets", ha="center", va="center")
        return fig

    pos = nx.spring_layout(g, seed=7)  # graine fixe : la disposition reste stable
    visited = set(step.visited) if step else set()
    frontier = set(step.frontier) if step else set()
    current = step.current if step else None
    path_nodes = set(path)
    path_edges = set(zip(path, path[1:], strict=False))
    examined = (step.current, step.neighbor) if step and step.current and step.neighbor else None

    colors, borders, widths = [], [], []
    for node in g.nodes:
        if node == current:
            colors.append(COLOR_CURRENT)
        elif node in path_nodes:
            colors.append(COLOR_PATH)
        elif node in frontier:
            colors.append(COLOR_FRONTIER)
        elif node in visited:
            colors.append(COLOR_VISITED)
        else:
            colors.append(COLOR_DEFAULT)
        if node == graph.start:
            borders.append(BORDER_START)
            widths.append(3.5)
        elif node == graph.goal:
            borders.append(BORDER_GOAL)
            widths.append(3.5)
        else:
            borders.append(BORDER_DEFAULT)
            widths.append(1)

    # arcs : normaux, arc examiné, chemin final
    normal = [e for e in g.edges if e not in path_edges and e != examined]
    highlighted = [(list(path_edges), "#16A34A", 3.5)]
    if examined is not None and examined in g.edges:
        highlighted.append(([examined], COLOR_CURRENT, 3))
    if normal:
        nx.draw_networkx_edges(
            g,
            pos,
            edgelist=normal,
            ax=ax,
            arrows=True,
            arrowstyle="-|>",
            arrowsize=18,
            node_size=NODE_SIZE,
            connectionstyle=CURVE,
            edge_color="#6B7280",
        )
    for edgelist, color, width in highlighted:
        if edgelist:
            nx.draw_networkx_edges(
                g,
                pos,
                edgelist=edgelist,
                ax=ax,
                arrows=True,
                arrowstyle="-|>",
                arrowsize=20,
                node_size=NODE_SIZE,
                connectionstyle=CURVE,
                edge_color=color,
                width=width,
            )

    nx.draw_networkx_nodes(
        g,
        pos,
        ax=ax,
        node_color=colors,
        edgecolors=borders,
        linewidths=widths,
        node_size=NODE_SIZE,
    )
    labels = {}
    for node in g.nodes:
        h = g.nodes[node].get("h")
        labels[node] = node if h is None else f"{node}\nh={fmt(h)}"
    nx.draw_networkx_labels(g, pos, labels=labels, ax=ax, font_size=9)

    # coûts des arcs (les boucles A→A ne sont pas étiquetées)
    edge_labels = {(u, v): fmt(c) for u, v, c in graph.edges() if u != v}
    if edge_labels:
        style = {
            "font_size": 8,
            "bbox": {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.85},
        }
        try:
            nx.draw_networkx_edge_labels(
                g, pos, edge_labels=edge_labels, ax=ax, connectionstyle=CURVE, **style
            )
        except TypeError:  # anciennes versions de NetworkX sans « connectionstyle »
            nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, ax=ax, **style)

    def dot(fill, border, width, label):
        return Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=fill,
            markeredgecolor=border,
            markeredgewidth=width,
            markersize=10,
            label=label,
        )

    fig.legend(
        handles=[
            dot(COLOR_CURRENT, BORDER_DEFAULT, 1, "Sommet courant"),
            dot(COLOR_FRONTIER, BORDER_DEFAULT, 1, "Frontière"),
            dot(COLOR_VISITED, BORDER_DEFAULT, 1, "Développé"),
            dot(COLOR_PATH, BORDER_DEFAULT, 1, "Chemin final"),
            dot(COLOR_DEFAULT, BORDER_START, 3, "Départ"),
            dot(COLOR_DEFAULT, BORDER_GOAL, 3, "Objectif"),
        ],
        loc="lower center",
        ncol=3,
        fontsize=8,
        frameon=False,
    )
    ax.margins(0.15)
    fig.subplots_adjust(bottom=0.17)
    return fig
