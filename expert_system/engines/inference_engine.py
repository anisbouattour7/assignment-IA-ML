from abc import ABC, abstractmethod

from expert_system.models.inference_result import InferenceResult
from expert_system.models.knowledge_base import KnowledgeBase


class InferenceEngine(ABC):
    """Contrat commun : chaque moteur reçoit la base et un objectif, et retourne un résultat."""

    method: str = ""

    @abstractmethod
    def infer(self, knowledge_base: KnowledgeBase, goal: str) -> InferenceResult: ...
