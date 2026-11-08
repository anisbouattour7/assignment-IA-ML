from dataclasses import dataclass

from expert_system.models.inference_step import ACTION_APPLY_RULE, InferenceStep


@dataclass(frozen=True)
class InferenceResult:
    """Résultat complet d'une exécution (identique pour les deux chaînages)."""

    goal: str
    method: str
    success: bool
    initial_facts: tuple[str, ...]
    derived_facts: tuple[str, ...]
    steps: tuple[InferenceStep, ...]
    message: str

    @property
    def rules_applied(self) -> tuple[str, ...]:
        """Identifiants des règles appliquées, dans l'ordre."""
        return tuple(s.rule_id for s in self.steps if s.action == ACTION_APPLY_RULE and s.rule_id)
