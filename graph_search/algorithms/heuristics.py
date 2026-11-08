import math
from collections import deque
from collections.abc import Mapping

import networkx as nx

from graph_search.algorithms.base import fmt
from graph_search.models.graph_model import GraphError, GraphModel


def reachable_nodes(graph: GraphModel, start: str) -> list[str]:
    """Sommets accessibles depuis le départ (départ inclus), en ordre de parcours."""
    seen = {start}
    order = [start]
    queue: deque[str] = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor, _cost in graph.successors(node):
            if neighbor not in seen:
                seen.add(neighbor)
                order.append(neighbor)
                queue.append(neighbor)
    return order


def _is_valid(value) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


def resolve_heuristic(
    graph: GraphModel,
    start: str,
    goal: str,
    heuristic: Mapping[str, float] | None = None,
) -> dict[str, float]:
    """Retourne h(n) pour tous les sommets accessibles depuis le départ.

    - sans `heuristic`, on lit les valeurs stockées dans le graphe ;
    - h(objectif) vaut 0 par défaut s'il n'est pas défini ;
    - seuls les sommets accessibles (donc susceptibles d'être évalués) doivent avoir un h ;
    - sinon GraphError, qui nomme les sommets concernés.
    """
    if heuristic is None:
        source: Mapping[str, float | None] = {n: graph.get_heuristic(n) for n in graph.nodes()}
    else:
        source = heuristic

    values: dict[str, float] = {}
    missing: list[str] = []
    invalid: list[str] = []
    for node in reachable_nodes(graph, start):
        value = source.get(node)
        if value is None:
            if node == goal:
                value = 0
            else:
                missing.append(node)
                continue
        if not _is_valid(value):
            invalid.append(node)
            continue
        values[node] = value

    errors: list[str] = []
    if missing:
        errors.append("Heuristique manquante pour : " + ", ".join(missing))
    if invalid:
        errors.append("Heuristique invalide (nombre ≥ 0 attendu) pour : " + ", ".join(invalid))
    if errors:
        raise GraphError(" ; ".join(errors))
    return values


def admissibility_violations(graph: GraphModel, goal: str, h: Mapping[str, float]) -> list[str]:
    """Sommets dont h(n) dépasse le coût optimal réel restant jusqu'à l'objectif.

    Le coût optimal restant est calculé par un Dijkstra sur le graphe inversé.
    Les sommets qui ne peuvent pas atteindre l'objectif sont ignorés.
    """
    true_costs = nx.single_source_dijkstra_path_length(
        graph.graph.reverse(copy=False), goal, weight="weight"
    )
    violations: list[str] = []
    for node, value in h.items():
        optimal = true_costs.get(node)
        if optimal is not None and value > optimal + 1e-9:
            violations.append(f"h({node}) = {fmt(value)} > coût optimal restant {fmt(optimal)}")
    return violations
