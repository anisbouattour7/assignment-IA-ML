import heapq
import itertools
from dataclasses import replace

from graph_search.algorithms.base import TraceBuilder, fmt
from graph_search.algorithms.informed_base import InformedSearchAlgorithm
from graph_search.models.search_result import SearchResult
from graph_search.models.search_step import (
    ACTION_DISCOVER,
    ACTION_EXPAND,
    ACTION_GOAL,
    ACTION_IGNORE,
    ACTION_INIT,
    ACTION_STOP,
)


class GreedyBestFirst(InformedSearchAlgorithm):
    """Recherche gloutonne : on développe le sommet qui paraît le plus proche (h minimal).

    Le coût déjà parcouru est ignoré : aucune garantie d'optimalité. Chaque sommet est
    mis dans la frontière une seule fois (h(n) ne dépend pas du chemin suivi).
    À h égal, le sommet découvert en premier passe en premier.
    """

    code = "Gloutonne"
    label = "Gloutonne — Greedy Best-First Search"
    priority = "File de priorité : on développe le sommet de plus petite heuristique h(n)."

    def _run(self, graph, start, goal, heuristic) -> SearchResult:
        h = heuristic
        counter = itertools.count()
        heap: list[tuple[float, int, str]] = [(h[start], next(counter), start)]
        discovered = {start}
        parent: dict[str, str | None] = {start: None}
        expanded: list[str] = []
        trace = TraceBuilder()

        def frontier_view() -> tuple[tuple[str, ...], tuple[float, ...]]:
            entries = sorted(heap)
            return tuple(n for _, _, n in entries), tuple(v for v, _, _ in entries)

        trace.add(
            ACTION_INIT,
            f"Initialisation : « {start} » avec h = {fmt(h[start])}.",
            frontier=(start,),
            frontier_costs=(h[start],),
            h=h[start],
        )

        while heap:
            _, _, current = heapq.heappop(heap)
            expanded.append(current)
            names, costs = frontier_view()
            trace.add(
                ACTION_EXPAND,
                f"Extraction de « {current} » (h = {fmt(h[current])}, "
                "plus petite valeur de la frontière).",
                current=current,
                frontier=names,
                frontier_costs=costs,
                visited=tuple(expanded),
                h=h[current],
                predecessor=parent[current],
            )
            if current == goal:
                trace.add(
                    ACTION_GOAL,
                    f"L'objectif « {goal} » est extrait de la frontière.",
                    current=current,
                    frontier=names,
                    frontier_costs=costs,
                    visited=tuple(expanded),
                    h=h[current],
                    predecessor=parent[current],
                )
                result = self._success(graph, start, goal, parent, trace, expanded)
                return replace(
                    result,
                    warnings=(
                        "La recherche gloutonne ne garantit pas l'optimalité : "
                        "le coût déjà parcouru n'est pas pris en compte.",
                    ),
                )

            for neighbor, _cost in graph.successors(current):
                if neighbor in discovered:
                    trace.add(
                        ACTION_IGNORE,
                        f"« {neighbor} » est déjà découvert : ignoré.",
                        current=current,
                        neighbor=neighbor,
                        frontier=names,
                        frontier_costs=costs,
                        visited=tuple(expanded),
                    )
                    continue
                discovered.add(neighbor)
                parent[neighbor] = current
                heapq.heappush(heap, (h[neighbor], next(counter), neighbor))
                names, costs = frontier_view()
                trace.add(
                    ACTION_DISCOVER,
                    f"« {neighbor} » découvert depuis « {current} » : h = {fmt(h[neighbor])}.",
                    current=current,
                    neighbor=neighbor,
                    frontier=names,
                    frontier_costs=costs,
                    visited=tuple(expanded),
                    h=h[neighbor],
                    predecessor=current,
                )

        trace.add(
            ACTION_STOP,
            "La frontière est vide : l'objectif est inaccessible.",
            visited=tuple(expanded),
        )
        return self._failure(start, goal, trace, expanded)
