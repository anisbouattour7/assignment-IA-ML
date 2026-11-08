from collections.abc import Mapping

from graph_search.algorithms.base import CATEGORY_INFORMED
from graph_search.algorithms.heuristics import resolve_heuristic
from graph_search.algorithms.registry import ALGORITHMS
from graph_search.models.graph_model import GraphError, GraphModel
from graph_search.models.search_config import SearchConfig
from graph_search.models.search_result import SearchResult


class SearchService:
    """Point d'entrée applicatif : valide la configuration, choisit l'algorithme, lance."""

    def validate(
        self,
        graph: GraphModel,
        config: SearchConfig,
        heuristic: Mapping[str, float] | None = None,
    ) -> list[str]:
        """Liste des erreurs bloquantes (vide si la recherche peut être lancée)."""
        errors = graph.validate()
        algo = ALGORITHMS.get(config.algorithm)
        if algo is None:
            errors.append(f"Algorithme inconnu : « {config.algorithm} ».")
        elif config.category is not None and config.category != algo.category:
            errors.append(
                f"L'algorithme « {config.algorithm} » n'appartient pas à la catégorie choisie."
            )
        if not graph.has_node(config.start):
            errors.append(f"Le sommet de départ « {config.start} » n'existe pas.")
        if not graph.has_node(config.goal):
            errors.append(f"Le sommet objectif « {config.goal} » n'existe pas.")

        if (
            algo is not None
            and algo.category == CATEGORY_INFORMED
            and graph.has_node(config.start)
            and graph.has_node(config.goal)
        ):
            try:
                resolve_heuristic(graph, config.start, config.goal, heuristic)
            except GraphError as exc:
                errors.append(str(exc))
        return errors

    def run(
        self,
        graph: GraphModel,
        config: SearchConfig,
        heuristic: Mapping[str, float] | None = None,
    ) -> SearchResult:
        """Lance la recherche ; sans `heuristic`, les h stockés dans le graphe sont utilisés."""
        errors = self.validate(graph, config, heuristic)
        if errors:
            raise GraphError(" ; ".join(errors))
        return ALGORITHMS[config.algorithm]().search(graph, config.start, config.goal, heuristic)
