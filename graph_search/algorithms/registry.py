from graph_search.algorithms.astar import AStar
from graph_search.algorithms.base import CATEGORY_INFORMED, CATEGORY_UNINFORMED, SearchAlgorithm
from graph_search.algorithms.bfs import BFS
from graph_search.algorithms.dfs import DFS
from graph_search.algorithms.greedy import GreedyBestFirst
from graph_search.algorithms.ucs import UCS

# Catalogue : code de l'algorithme -> classe (l'ordre est celui de l'interface)
ALGORITHMS: dict[str, type[SearchAlgorithm]] = {
    algo.code: algo for algo in (BFS, DFS, UCS, GreedyBestFirst, AStar)
}

CATEGORY_LABELS = {
    CATEGORY_UNINFORMED: "Recherche non informée (aveugle)",
    CATEGORY_INFORMED: "Recherche informée (heuristique)",
}


def algorithms_in(category: str) -> list[type[SearchAlgorithm]]:
    """Algorithmes d'une catégorie, dans l'ordre d'affichage."""
    return [algo for algo in ALGORITHMS.values() if algo.category == category]
