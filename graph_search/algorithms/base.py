from abc import ABC, abstractmethod
from collections.abc import Mapping

from graph_search.models.graph_model import GraphError, GraphModel
from graph_search.models.search_result import SearchResult
from graph_search.models.search_step import SearchStep

CATEGORY_UNINFORMED = "non_informee"
CATEGORY_INFORMED = "informee"


def fmt(value: float) -> str:
    """Affiche 4 pour 4.0 et évite les artefacts de flottants."""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.6g}"


def reconstruct_path(parent: Mapping[str, str | None], goal: str) -> list[str]:
    """Remonte les prédécesseurs de l'objectif jusqu'au départ."""
    path: list[str] = []
    node: str | None = goal
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


class TraceBuilder:
    """Construit la liste numérotée des étapes."""

    def __init__(self) -> None:
        self.steps: list[SearchStep] = []

    def add(self, action: str, explanation: str, **fields) -> None:
        self.steps.append(
            SearchStep(index=len(self.steps) + 1, action=action, explanation=explanation, **fields)
        )


class SearchAlgorithm(ABC):
    """Contrat commun : search(graph, start, goal, heuristic) -> SearchResult."""

    code: str = ""  # ex. "BFS"
    label: str = ""  # libellé affiché dans l'interface
    category: str = ""  # CATEGORY_UNINFORMED ou CATEGORY_INFORMED
    priority: str = ""  # rappel de la priorité utilisée

    def search(
        self,
        graph: GraphModel,
        start: str,
        goal: str,
        heuristic: Mapping[str, float] | None = None,
    ) -> SearchResult:
        self._validate(graph, start, goal)
        return self._run(graph, start, goal, heuristic)

    @abstractmethod
    def _run(
        self,
        graph: GraphModel,
        start: str,
        goal: str,
        heuristic: Mapping[str, float] | None,
    ) -> SearchResult: ...

    def _validate(self, graph: GraphModel, start: str, goal: str) -> None:
        errors: list[str] = []
        if not graph.nodes():
            errors.append("Le graphe est vide : ajoutez au moins un sommet.")
        if not graph.has_node(start):
            errors.append(f"Le sommet de départ « {start} » n'existe pas.")
        if not graph.has_node(goal):
            errors.append(f"Le sommet objectif « {goal} » n'existe pas.")
        if errors:
            raise GraphError(" ; ".join(errors))

    def _success(
        self,
        graph: GraphModel,
        start: str,
        goal: str,
        parent: Mapping[str, str | None],
        trace: TraceBuilder,
        expanded: list[str],
    ) -> SearchResult:
        path = reconstruct_path(parent, goal)
        cost = graph.path_cost(path)  # coût réel recalculé à partir des poids du graphe
        return SearchResult(
            algorithm=self.code,
            start=start,
            goal=goal,
            found=True,
            path=tuple(path),
            total_cost=cost,
            steps=tuple(trace.steps),
            expanded_nodes=tuple(expanded),
            message=f"Chemin trouvé par {self.code} : {' → '.join(path)} (coût total {fmt(cost)}).",
        )

    def _failure(
        self, start: str, goal: str, trace: TraceBuilder, expanded: list[str]
    ) -> SearchResult:
        return SearchResult(
            algorithm=self.code,
            start=start,
            goal=goal,
            found=False,
            path=(),
            total_cost=None,
            steps=tuple(trace.steps),
            expanded_nodes=tuple(expanded),
            message=f"Aucun chemin trouvé de « {start} » à « {goal} » avec {self.code}.",
        )
