import json
import math
from collections.abc import Sequence
from pathlib import Path

import networkx as nx


class GraphError(ValueError):
    """Entrée invalide : graphe, coût, heuristique ou paramètres de recherche."""


def _check_number(value, label: str):
    """Accepte un nombre fini et non négatif (les booléens sont refusés)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GraphError(f"{label} doit être un nombre.")
    if math.isnan(value) or math.isinf(value):
        raise GraphError(f"{label} doit être un nombre fini.")
    if value < 0:
        raise GraphError(f"{label} ne peut pas être négatif.")
    return value


class GraphModel:
    """Graphe orienté pondéré. Sommet = chaîne unique ; arc = attribut « weight » ;
    heuristique = attribut « h » du sommet. Un arc A→B ne crée pas B→A.

    L'ordre des successeurs d'un sommet est l'ordre d'ajout de ses arcs (stable).
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.start: str | None = None
        self.goal: str | None = None

    # ---------- sommets ----------
    def add_node(self, name: str, h: float | None = None) -> None:
        if not isinstance(name, str) or not name.strip():
            raise GraphError("Le nom d'un sommet ne peut pas être vide.")
        name = name.strip()
        if name in self.graph:
            raise GraphError(f"Le sommet « {name} » existe déjà.")
        if h is not None:
            _check_number(h, f"h({name})")
        self.graph.add_node(name, h=h)

    def remove_node(self, name: str) -> None:
        name = self._require_node(name)
        self.graph.remove_node(name)  # supprime aussi les arcs incidents
        if self.start == name:
            self.start = None
        if self.goal == name:
            self.goal = None

    def has_node(self, name: str) -> bool:
        return name in self.graph

    def nodes(self) -> list[str]:
        return list(self.graph.nodes)

    # ---------- arcs ----------
    def add_edge(self, source: str, target: str, cost: float) -> None:
        source = self._require_node(source)
        target = self._require_node(target)
        cost = _check_number(cost, f"Le coût de {source}→{target}")
        if self.graph.has_edge(source, target):
            raise GraphError(f"L'arc {source}→{target} existe déjà.")
        self.graph.add_edge(source, target, weight=cost)

    def remove_edge(self, source: str, target: str) -> None:
        if not self.graph.has_edge(source, target):
            raise GraphError(f"L'arc {source}→{target} n'existe pas.")
        self.graph.remove_edge(source, target)

    def has_edge(self, source: str, target: str) -> bool:
        return self.graph.has_edge(source, target)

    def edge_cost(self, source: str, target: str) -> float:
        if not self.graph.has_edge(source, target):
            raise GraphError(f"L'arc {source}→{target} n'existe pas.")
        return self.graph[source][target]["weight"]

    def edges(self) -> list[tuple[str, str, float]]:
        return [(u, v, data["weight"]) for u, v, data in self.graph.edges(data=True)]

    def successors(self, node: str) -> list[tuple[str, float]]:
        """Voisins sortants (sommet, coût), dans l'ordre d'ajout des arcs."""
        node = self._require_node(node)
        return [(v, self.graph[node][v]["weight"]) for v in self.graph.successors(node)]

    # ---------- heuristique ----------
    def set_heuristic(self, node: str, value: float | None) -> None:
        """Définit h(node) ; None efface la valeur."""
        node = self._require_node(node)
        if value is not None:
            _check_number(value, f"h({node})")
        self.graph.nodes[node]["h"] = value

    def get_heuristic(self, node: str) -> float | None:
        node = self._require_node(node)
        return self.graph.nodes[node].get("h")

    # ---------- départ et objectif ----------
    def set_start(self, name: str) -> None:
        self.start = self._require_node(name)

    def set_goal(self, name: str) -> None:
        self.goal = self._require_node(name)

    # ---------- chemins ----------
    def path_cost(self, path: Sequence[str]) -> float:
        """Somme des coûts des arcs consécutifs ; erreur si un arc n'existe pas."""
        if not path:
            raise GraphError("Un chemin doit contenir au moins un sommet.")
        for node in path:
            if node not in self.graph:
                raise GraphError(f"Le sommet « {node} » n'existe pas.")
        total = 0
        for u, v in zip(path, path[1:], strict=False):
            if not self.graph.has_edge(u, v):
                raise GraphError(f"Le chemin utilise un arc inexistant : {u}→{v}.")
            total += self.graph[u][v]["weight"]
        return total

    # ---------- validation ----------
    def validate(self) -> list[str]:
        """Liste des erreurs de cohérence (vide si le graphe est exploitable)."""
        errors: list[str] = []
        if self.graph.number_of_nodes() == 0:
            errors.append("Le graphe est vide : ajoutez au moins un sommet.")
        for u, v, data in self.graph.edges(data=True):
            try:
                _check_number(data.get("weight"), f"Le coût de {u}→{v}")
            except GraphError as exc:
                errors.append(str(exc))
        return errors

    # ---------- persistance JSON (format de l'annexe A du dossier) ----------
    def to_dict(self) -> dict:
        nodes = []
        for name in self.graph.nodes:
            entry: dict = {"id": name}
            h = self.graph.nodes[name].get("h")
            if h is not None:
                entry["h"] = h
            nodes.append(entry)
        data: dict = {
            "nodes": nodes,
            "edges": [{"source": u, "target": v, "cost": c} for u, v, c in self.edges()],
        }
        if self.start is not None:
            data["start"] = self.start
        if self.goal is not None:
            data["goal"] = self.goal
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "GraphModel":
        model = cls()
        try:
            for node in data.get("nodes", []):
                model.add_node(node["id"], node.get("h"))
            for edge in data.get("edges", []):
                model.add_edge(edge["source"], edge["target"], edge["cost"])
            if data.get("start") is not None:
                model.set_start(data["start"])
            if data.get("goal") is not None:
                model.set_goal(data["goal"])
        except (KeyError, TypeError, AttributeError) as exc:
            raise GraphError(f"Format de graphe invalide : {exc!r}") from exc
        return model

    @classmethod
    def load_json(cls, path: str | Path) -> "GraphModel":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    # ---------- interne ----------
    def _require_node(self, name: str) -> str:
        if isinstance(name, str):
            name = name.strip()
        if name not in self.graph:
            raise GraphError(f"Le sommet « {name} » n'existe pas.")
        return name
