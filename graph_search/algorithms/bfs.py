from collections import deque

from graph_search.algorithms.base import CATEGORY_UNINFORMED, SearchAlgorithm, TraceBuilder
from graph_search.models.search_result import SearchResult
from graph_search.models.search_step import (
    ACTION_DISCOVER,
    ACTION_EXPAND,
    ACTION_GOAL,
    ACTION_IGNORE,
    ACTION_INIT,
    ACTION_STOP,
)


class BFS(SearchAlgorithm):
    """Parcours en largeur : file FIFO, niveau par niveau.

    Trouve un chemin avec un nombre minimal d'arcs, mais pas forcément de coût minimal.
    """

    code = "BFS"
    label = "BFS — Parcours en largeur"
    category = CATEGORY_UNINFORMED
    priority = "File FIFO : on développe d'abord les sommets les moins profonds (en nombre d'arcs)."

    def _run(self, graph, start, goal, heuristic=None) -> SearchResult:
        frontier: deque[str] = deque([start])
        discovered = {start}  # sommets déjà découverts (évite les cycles)
        parent: dict[str, str | None] = {start: None}
        expanded: list[str] = []
        trace = TraceBuilder()
        trace.add(
            ACTION_INIT,
            f"Initialisation : la file contient le départ « {start} ».",
            frontier=(start,),
        )

        while frontier:
            current = frontier.popleft()
            expanded.append(current)
            trace.add(
                ACTION_EXPAND,
                f"Extraction de « {current} » en tête de file (FIFO).",
                current=current,
                frontier=tuple(frontier),
                visited=tuple(expanded),
                predecessor=parent[current],
            )
            if current == goal:
                trace.add(
                    ACTION_GOAL,
                    f"L'objectif « {goal} » est atteint.",
                    current=current,
                    frontier=tuple(frontier),
                    visited=tuple(expanded),
                    predecessor=parent[current],
                )
                return self._success(graph, start, goal, parent, trace, expanded)

            for neighbor, _cost in graph.successors(current):
                if neighbor in discovered:
                    trace.add(
                        ACTION_IGNORE,
                        f"« {neighbor} » est déjà découvert : ignoré.",
                        current=current,
                        neighbor=neighbor,
                        frontier=tuple(frontier),
                        visited=tuple(expanded),
                    )
                    continue
                discovered.add(neighbor)
                parent[neighbor] = current
                frontier.append(neighbor)
                trace.add(
                    ACTION_DISCOVER,
                    f"« {neighbor} » découvert depuis « {current} » : ajouté à la fin de la file.",
                    current=current,
                    neighbor=neighbor,
                    frontier=tuple(frontier),
                    visited=tuple(expanded),
                    predecessor=current,
                )

        trace.add(
            ACTION_STOP,
            "La file est vide : l'objectif est inaccessible.",
            visited=tuple(expanded),
        )
        return self._failure(start, goal, trace, expanded)
