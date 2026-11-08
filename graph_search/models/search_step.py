from dataclasses import dataclass

# Types d'actions de la trace
ACTION_INIT = "initialisation"
ACTION_EXPAND = "developpement"  # extraction du sommet courant de la frontière
ACTION_DISCOVER = "decouverte"  # un voisin est ajouté à la frontière
ACTION_UPDATE = "mise_a_jour"  # meilleur coût trouvé pour un sommet (relaxation)
ACTION_IGNORE = "ignore"  # un voisin n'apporte rien
ACTION_GOAL = "objectif_atteint"
ACTION_STOP = "arret"  # frontière vide : aucun chemin


@dataclass(frozen=True)
class SearchStep:
    """Une étape explicable de la recherche.

    - frontier : sommets découverts mais pas encore développés, dans l'ordre où
    l'algorithme les prendra ;
    - frontier_costs : priorité de chaque sommet de la frontière, alignée sur frontier
      (g pour UCS, h pour Gloutonne, f pour A*) ;
    - visited : sommets déjà développés, dans l'ordre ;
    - g, h, f : valeurs utiles à l'étape (h et f serviront aux algorithmes informés).
    """

    index: int
    action: str
    explanation: str
    current: str | None = None
    neighbor: str | None = None
    frontier: tuple[str, ...] = ()
    frontier_costs: tuple[float, ...] = ()
    visited: tuple[str, ...] = ()
    g: float | None = None
    h: float | None = None
    f: float | None = None
    predecessor: str | None = None
