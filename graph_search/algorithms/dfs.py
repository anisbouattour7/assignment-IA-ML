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


class DFS(SearchAlgorithm):
    """Parcours en profondeur : pile LIFO, on approfondit une branche avant de revenir.

    Ne garantit ni le minimum d'arcs, ni le coût minimal.
    Le prédécesseur d'un sommet est fixé à son développement (vrai arbre DFS).
    """

    code = "DFS"
    label = "DFS — Parcours en profondeur"
    category = CATEGORY_UNINFORMED
    priority = "Pile LIFO : on développe le dernier sommet ajouté."

    def _run(self, graph, start, goal, heuristic=None) -> SearchResult:
        stack: list[tuple[str, str | None]] = [(start, None)]  # (sommet, prédécesseur)
        visited: set[str] = set()  # sommets développés
        parent: dict[str, str | None] = {}
        expanded: list[str] = []
        trace = TraceBuilder()

        def frontier_view() -> tuple[str, ...]:
            """Sommets en attente, du prochain à développer au dernier (sans doublons)."""
            seen: set[str] = set()
            view: list[str] = []
            for node, _ in reversed(stack):
                if node not in visited and node not in seen:
                    view.append(node)
                    seen.add(node)
            return tuple(view)

        trace.add(
            ACTION_INIT,
            f"Initialisation : la pile contient le départ « {start} ».",
            frontier=(start,),
        )

        while stack:
            current, pred = stack.pop()
            if current in visited:
                continue  # entrée de pile obsolète : sommet déjà développé
            visited.add(current)
            expanded.append(current)
            parent[current] = pred
            trace.add(
                ACTION_EXPAND,
                f"Dépilement de « {current} » (dernier sommet ajouté à la pile).",
                current=current,
                frontier=frontier_view(),
                visited=tuple(expanded),
                predecessor=pred,
            )
            if current == goal:
                trace.add(
                    ACTION_GOAL,
                    f"L'objectif « {goal} » est atteint.",
                    current=current,
                    frontier=frontier_view(),
                    visited=tuple(expanded),
                    predecessor=pred,
                )
                return self._success(graph, start, goal, parent, trace, expanded)

            to_push: list[str] = []
            for neighbor, _cost in graph.successors(current):
                if neighbor in visited:
                    trace.add(
                        ACTION_IGNORE,
                        f"« {neighbor} » est déjà développé : ignoré.",
                        current=current,
                        neighbor=neighbor,
                        frontier=frontier_view(),
                        visited=tuple(expanded),
                    )
                else:
                    to_push.append(neighbor)
            # On empile en ordre inverse pour que le premier successeur soit développé en premier
            for neighbor in reversed(to_push):
                stack.append((neighbor, current))
            if to_push:
                names = ", ".join(f"« {n} »" for n in to_push)
                trace.add(
                    ACTION_DISCOVER,
                    f"Ajout à la pile depuis « {current} » : {names} "
                    f"(« {to_push[0]} » sera développé en premier).",
                    current=current,
                    frontier=frontier_view(),
                    visited=tuple(expanded),
                    predecessor=current,
                )

        trace.add(
            ACTION_STOP,
            "La pile est vide : l'objectif est inaccessible.",
            visited=tuple(expanded),
        )
        return self._failure(start, goal, trace, expanded)
