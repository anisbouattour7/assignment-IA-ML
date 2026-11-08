from collections.abc import Mapping

from graph_search.algorithms.base import CATEGORY_INFORMED, SearchAlgorithm
from graph_search.algorithms.heuristics import resolve_heuristic
from graph_search.models.graph_model import GraphModel
from graph_search.models.search_result import SearchResult


class InformedSearchAlgorithm(SearchAlgorithm):
    """Socle des algorithmes informés : valide d'abord les heuristiques, puis cherche.

    `_run` reçoit un dictionnaire h déjà vérifié pour tous les sommets accessibles.
    """

    category = CATEGORY_INFORMED

    def search(
        self,
        graph: GraphModel,
        start: str,
        goal: str,
        heuristic: Mapping[str, float] | None = None,
    ) -> SearchResult:
        self._validate(graph, start, goal)
        values = resolve_heuristic(graph, start, goal, heuristic)
        return self._run(graph, start, goal, values)
