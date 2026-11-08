from dataclasses import dataclass


@dataclass(frozen=True)
class SearchConfig:
    """Paramètres d'une recherche. `algorithm` est le code : BFS, DFS, UCS, Gloutonne, A*."""

    start: str
    goal: str
    algorithm: str
    category: str | None = None  # si renseignée, doit correspondre à l'algorithme
