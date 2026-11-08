import heapq
import itertools
from dataclasses import replace

from graph_search.algorithms.base import TraceBuilder, fmt
from graph_search.algorithms.heuristics import admissibility_violations
from graph_search.algorithms.informed_base import InformedSearchAlgorithm
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


class AStar(InformedSearchAlgorithm):
    """A* : on développe le sommet de plus petit f(n) = g(n) + h(n).

    - Quand un meilleur g est trouvé, le prédécesseur est mis à jour et le sommet est
      réinséré ; s'il avait déjà été développé, il est ROUVERT (utile si h est
      admissible mais non cohérente).
    - Arrêt quand l'objectif est extrait de la file avec son meilleur coût.
    - L'optimalité n'est garantie que si h est admissible : on le vérifie et on
      ajoute un avertissement dans le résultat sinon.
    - À f égal, le sommet inséré en premier passe en premier.
    """

    code = "A*"
    label = "A* — A-star"
    priority = "File de priorité : on développe le sommet de plus petit f(n) = g(n) + h(n)."

    def _run(self, graph, start, goal, heuristic) -> SearchResult:
        h = heuristic
        violations = admissibility_violations(graph, goal, h)
        warnings: tuple[str, ...] = ()
        if violations:
            warnings = (
                "Heuristique non admissible ("
                + " ; ".join(violations)
                + ") : l'optimalité de A* n'est pas garantie.",
            )

        counter = itertools.count()
        # entrée : (f, ordre d'insertion, g, sommet)
        heap: list[tuple[float, int, float, str]] = [(h[start], next(counter), 0, start)]
        best_g: dict[str, float] = {start: 0}
        parent: dict[str, str | None] = {start: None}
        closed: set[str] = set()
        expanded: list[str] = []  # peut contenir un sommet deux fois (réouverture)
        trace = TraceBuilder()

        def frontier_view() -> tuple[tuple[str, ...], tuple[float, ...]]:
            """Entrées valides de la file (sans entrées obsolètes), triées par f."""
            entries = sorted(e for e in heap if e[2] == best_g[e[3]])
            return tuple(e[3] for e in entries), tuple(e[0] for e in entries)

        def visited_view() -> tuple[str, ...]:
            return tuple(dict.fromkeys(expanded))

        trace.add(
            ACTION_INIT,
            f"Initialisation : « {start} » avec g = 0, h = {fmt(h[start])}, f = {fmt(h[start])}.",
            frontier=(start,),
            frontier_costs=(h[start],),
            g=0,
            h=h[start],
            f=h[start],
        )

        while heap:
            f, _, g, current = heapq.heappop(heap)
            if g != best_g[current]:
                continue  # entrée obsolète : un meilleur g a été trouvé depuis
            closed.add(current)
            expanded.append(current)
            names, costs = frontier_view()
            trace.add(
                ACTION_EXPAND,
                f"Extraction de « {current} » (g = {fmt(g)}, h = {fmt(h[current])}, f = {fmt(f)}).",
                current=current,
                frontier=names,
                frontier_costs=costs,
                visited=visited_view(),
                g=g,
                h=h[current],
                f=f,
                predecessor=parent[current],
            )
            if current == goal:
                trace.add(
                    ACTION_GOAL,
                    f"L'objectif « {goal} » est extrait avec le meilleur coût g = {fmt(g)}.",
                    current=current,
                    frontier=names,
                    frontier_costs=costs,
                    visited=visited_view(),
                    g=g,
                    h=h[current],
                    f=f,
                    predecessor=parent[current],
                )
                result = self._success(graph, start, goal, parent, trace, expanded)
                return replace(result, warnings=warnings)

            for neighbor, weight in graph.successors(current):
                tentative = g + weight
                known = best_g.get(neighbor)
                if known is not None and tentative >= known:
                    trace.add(
                        ACTION_IGNORE,
                        f"« {neighbor} » : g = {fmt(tentative)} n'améliore pas "
                        f"le coût connu ({fmt(known)}).",
                        current=current,
                        neighbor=neighbor,
                        frontier=names,
                        frontier_costs=costs,
                        visited=visited_view(),
                    )
                    continue

                reopened = neighbor in closed
                best_g[neighbor] = tentative
                parent[neighbor] = current
                f_new = tentative + h[neighbor]
                heapq.heappush(heap, (f_new, next(counter), tentative, neighbor))
                names, costs = frontier_view()
                if known is None:
                    action = ACTION_DISCOVER
                    text = (
                        f"« {neighbor} » découvert : g = {fmt(g)} + {fmt(weight)} = "
                        f"{fmt(tentative)}, h = {fmt(h[neighbor])}, f = {fmt(f_new)}."
                    )
                else:
                    action = ACTION_UPDATE
                    kind = "Réouverture de" if reopened else "Meilleur chemin vers"
                    text = (
                        f"{kind} « {neighbor} » via « {current} » : g passe de {fmt(known)} "
                        f"à {fmt(tentative)}, f = {fmt(f_new)}."
                    )
                trace.add(
                    action,
                    text,
                    current=current,
                    neighbor=neighbor,
                    frontier=names,
                    frontier_costs=costs,
                    visited=visited_view(),
                    g=tentative,
                    h=h[neighbor],
                    f=f_new,
                    predecessor=current,
                )

        trace.add(
            ACTION_STOP,
            "La file de priorité est vide : l'objectif est inaccessible.",
            visited=visited_view(),
        )
        return replace(self._failure(start, goal, trace, expanded), warnings=warnings)
