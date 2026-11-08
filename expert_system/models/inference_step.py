from dataclasses import dataclass

# Types d'étapes de la trace (le chaînage arrière en ajoutera d'autres)
ACTION_GOAL_KNOWN = "objectif_connu"  # l'objectif figure déjà dans les faits
ACTION_APPLY_RULE = "regle_appliquee"  # une règle produit un nouveau fait
ACTION_GOAL_REACHED = "objectif_atteint"  # l'objectif vient d'être démontré
ACTION_STOP = "arret"  # plus aucune règle utile : échec

# --- Types d'étapes propres au chaînage arrière ---
ACTION_SUBGOAL = "sous_objectif"  # on cherche à démontrer un (sous-)objectif
ACTION_TRY_RULE = "regle_essayee"  # une règle candidate est essayée
ACTION_FACT_FOUND = "fait_trouve"  # sous-objectif déjà connu (fait ou déjà démontré)
ACTION_RULE_FAILED = "regle_echec"  # une règle candidate échoue
ACTION_NO_RULE = "aucune_regle"  # ni fait, ni règle pour conclure ce but
ACTION_CYCLE = "cycle_detecte"  # boucle détectée : branche abandonnée


@dataclass(frozen=True)
class InferenceStep:
    """Une étape explicable du raisonnement."""

    number: int
    action: str
    rule_id: str | None = None
    matched_facts: tuple[str, ...] = ()
    derived_fact: str | None = None
    explanation: str = ""
    depth: int = 0  # profondeur dans l'arbre de preuve (0 pour le chaînage avant)
