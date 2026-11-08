import heapq
import itertools
import math

from graph_search.algorithms.base import (
    CATEGORY_UNINFORMED,
    SearchAlgorithm,
    TraceBuilder,
    fmt,
)
from graph_search.models.search_result import SearchResult
from graph_search.models.search_step import (
    ACTION_DISCOVER,
    ACTION_EXPAND,
    ACTION_GOAL,
    ACTION_IGNORE,
    ACTION_INIT,
    ACTION_STOP,
    ACTION_UPDATE,
)


class UCS(SearchAlgorithm):
    """Recherche à coût uniforme : on développe le sommet de plus petit g(n).

    Non informée (aucune heuristique). Optimale pour des coûts non négatifs.
    L'arrêt se fait quand l'objectif est EXTRAIT de la file, pas quand il est découvert.
    À g égal, le sommet découvert (ou mis à jour) en premier passe en premier.
    """

    code = "UCS"
    label = "UCS — Coût uniforme"
    category = CATEGORY_UNINFORMED
    priority = "File de priorité : on développe le sommet de plus petit coût cumulé g(n)."

    def _run(self, graph, start, goal, heuristic=None) -> SearchResult:
        counter = itertools.count()  # départage stable des priorités égales
        heap: list[tuple[float, int, str]] = [(0, next(counter), start)]
        best: dict[str, float] = {start: 0}  # meilleur g connu
        parent: dict[str, str | None] = {start: None}
        closed: set[str] = set()  # sommets développés
        expanded: list[str] = []
        trace = TraceBuilder()

        def frontier_view() -> tuple[tuple[str, ...], tuple[float, ...]]:
            """Entrées valides de la file (sans entrées obsolètes), triées par priorité."""
            entries = sorted(e for e in heap if e[2] not in closed and e[0] == best[e[2]])
            return tuple(n for _, _, n in entries), tuple(c for c, _, _ in entries)

        trace.add(
            ACTION_INIT,
            f"Initialisation : « {start} » avec g = 0.",
            frontier=(start,),
            frontier_costs=(0,),
            g=0,
        )

        while heap:
            cost, _, current = heapq.heappop(heap)
            if current in closed or cost != best[current]:
                continue  # entrée obsolète (un meilleur coût a été trouvé depuis)
            closed.add(current)
            expanded.append(current)
            names, costs = frontier_view()
            trace.add(
                ACTION_EXPAND,
                f"Extraction de « {current} » (g = {fmt(cost)}, plus petit coût de la frontière).",
                current=current,
                frontier=names,
                frontier_costs=costs,
                visited=tuple(expanded),
                g=cost,
                predecessor=parent[current],
            )
            if current == goal:
                trace.add(
                    ACTION_GOAL,
                    f"L'objectif « {goal} » est extrait avec le coût minimal g = {fmt(cost)}.",
                    current=current,
                    frontier=names,
                    frontier_costs=costs,
                    visited=tuple(expanded),
                    g=cost,
                    predecessor=parent[current],
                )
                return self._success(graph, start, goal, parent, trace, expanded)

            for neighbor, weight in graph.successors(current):
                new_cost = cost + weight
                if neighbor in closed:
                    trace.add(
                        ACTION_IGNORE,
                        f"« {neighbor} » est déjà développé : ignoré.",
                        current=current,
                        neighbor=neighbor,
                        frontier=names,
                        frontier_costs=costs,
                        visited=tuple(expanded),
                    )
                elif new_cost < best.get(neighbor, math.inf):
                    old = best.get(neighbor)
                    best[neighbor] = new_cost
                    parent[neighbor] = current
                    heapq.heappush(heap, (new_cost, next(counter), neighbor))
                    names, costs = frontier_view()
                    if old is None:
                        action = ACTION_DISCOVER
                        text = (
                            f"« {neighbor} » découvert : g = {fmt(cost)} + {fmt(weight)} "
                            f"= {fmt(new_cost)}."
                        )
                    else:
                        action = ACTION_UPDATE
                        text = (
                            f"Meilleur chemin vers « {neighbor} » via « {current} » : "
                            f"g passe de {fmt(old)} à {fmt(new_cost)}."
                        )
                    trace.add(
                        action,
                        text,
                        current=current,
                        neighbor=neighbor,
                        frontier=names,
                        frontier_costs=costs,
                        visited=tuple(expanded),
                        g=new_cost,
                        predecessor=current,
                    )
                else:
                    trace.add(
                        ACTION_IGNORE,
                        f"« {neighbor} » : g = {fmt(new_cost)} n'améliore pas "
                        f"le coût connu ({fmt(best[neighbor])}).",
                        current=current,
                        neighbor=neighbor,
                        frontier=names,
                        frontier_costs=costs,
                        visited=tuple(expanded),
                    )

        trace.add(
            ACTION_STOP,
            "La file de priorité est vide : l'objectif est inaccessible.",
            visited=tuple(expanded),
        )
        return self._failure(start, goal, trace, expanded)
