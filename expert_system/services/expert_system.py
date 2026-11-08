from expert_system.engines.backward_chaining import BackwardChaining
from expert_system.engines.forward_chaining import ForwardChaining
from expert_system.engines.inference_engine import InferenceEngine
from expert_system.models.inference_result import InferenceResult
from expert_system.models.knowledge_base import KnowledgeBase

METHOD_FORWARD = "avant"
METHOD_BACKWARD = "arriere"
METHOD_LABELS = {METHOD_FORWARD: "Chaînage avant", METHOD_BACKWARD: "Chaînage arrière"}

_ENGINES: dict[str, type[InferenceEngine]] = {
    METHOD_FORWARD: ForwardChaining,
    METHOD_BACKWARD: BackwardChaining,
}


class ExpertSystemError(ValueError):
    """Entrée invalide (objectif vide, méthode inconnue, base incohérente)."""


class ExpertSystem:
    """Point d'entrée applicatif : valide l'entrée, choisit le moteur, lance l'inférence."""

    def __init__(self, knowledge_base: KnowledgeBase | None = None) -> None:
        self.knowledge_base = knowledge_base if knowledge_base is not None else KnowledgeBase()

    def is_goal_known(self, goal: str) -> bool:
        """Vrai si l'objectif figure déjà dans les faits initiaux (SE-04)."""
        return goal.strip() in self.knowledge_base.fact_names()

    def run(self, goal: str, method: str) -> InferenceResult:
        goal = goal.strip()
        if not goal:
            raise ExpertSystemError("L'objectif ne peut pas être vide.")
        engine_class = _ENGINES.get(method)
        if engine_class is None:
            raise ExpertSystemError(f"Méthode de chaînage inconnue : « {method} ».")
        errors = self.knowledge_base.validate()
        if errors:
            raise ExpertSystemError("Base de connaissances invalide : " + " ; ".join(errors))
        # Chaque exécution repart des faits initiaux (les moteurs travaillent sur une copie)
        return engine_class().infer(self.knowledge_base, goal)
