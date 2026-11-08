from dataclasses import dataclass

from graph_search.models.search_step import SearchStep


@dataclass(frozen=True)
class SearchResult:
    """Résultat commun à tous les algorithmes."""

    algorithm: str
    start: str
    goal: str
    found: bool
    path: tuple[str, ...]
    total_cost: float | None  # None si aucun chemin : on n'invente jamais un coût
    steps: tuple[SearchStep, ...]
    expanded_nodes: tuple[str, ...]
    message: str
    warnings: tuple[str, ...] = ()  # avertissements (heuristique non admissible, non-optimalité...)

    @property
    def expanded_count(self) -> int:
        return len(self.expanded_nodes)
