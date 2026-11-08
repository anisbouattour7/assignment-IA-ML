from expert_system.engines.inference_engine import InferenceEngine
from expert_system.models.inference_result import InferenceResult
from expert_system.models.inference_step import (
    ACTION_APPLY_RULE,
    ACTION_GOAL_KNOWN,
    ACTION_GOAL_REACHED,
    ACTION_STOP,
    InferenceStep,
)
from expert_system.models.knowledge_base import KnowledgeBase


class ForwardChaining(InferenceEngine):
    """Chaînage avant : part des faits initiaux et applique les règles jusqu'à l'objectif.

    Stratégie (déterministe) : à chaque cycle, on parcourt les règles dans l'ordre et on
    applique la première règle applicable qui produit un NOUVEAU fait, puis on repart du
    début. Le moteur s'arrête dès que l'objectif est atteint ou qu'aucune règle n'apporte
    plus de nouveau fait (ce qui garantit la terminaison, même en cas de cycle de règles).
    """

    method = "chaînage avant"

    def infer(self, knowledge_base: KnowledgeBase, goal: str) -> InferenceResult:
        goal = goal.strip()
        initial = tuple(f.name for f in knowledge_base.get_facts())
        working = set(initial)  # copie de travail : la base n'est jamais modifiée
        derived: list[str] = []
        steps: list[InferenceStep] = []

        def add_step(action: str, **kwargs) -> None:
            steps.append(InferenceStep(number=len(steps) + 1, action=action, **kwargs))

        def result(success: bool, message: str) -> InferenceResult:
            return InferenceResult(
                goal=goal,
                method=self.method,
                success=success,
                initial_facts=initial,
                derived_facts=tuple(derived),
                steps=tuple(steps),
                message=message,
            )

        # Cas 1 : objectif déjà connu, aucune règle nécessaire
        if goal in working:
            add_step(
                ACTION_GOAL_KNOWN,
                derived_fact=goal,
                explanation=f"« {goal} » figure déjà dans les faits initiaux : aucune règle nécessaire.",
            )
            return result(True, f"Objectif « {goal} » déjà présent dans la base de faits.")

        rules = knowledge_base.get_rules()
        while True:
            progress = False
            for rule in rules:
                if rule.conclusion in working:
                    continue  # n'apporterait aucun nouveau fait
                if not rule.is_applicable(working):
                    continue
                working.add(rule.conclusion)
                derived.append(rule.conclusion)
                add_step(
                    ACTION_APPLY_RULE,
                    rule_id=rule.id,
                    matched_facts=rule.conditions,
                    derived_fact=rule.conclusion,
                    explanation=(
                        f"{rule.id} appliquée : {' ET '.join(rule.conditions)} ⇒ {rule.conclusion}"
                    ),
                )
                progress = True
                if rule.conclusion == goal:
                    add_step(
                        ACTION_GOAL_REACHED,
                        derived_fact=goal,
                        explanation=f"Objectif « {goal} » atteint.",
                    )
                    return result(
                        True,
                        f"Objectif « {goal} » démontré par chaînage avant "
                        f"({len(derived)} fait(s) déduit(s)).",
                    )
                break  # on repart du début de la liste des règles
            if not progress:
                break

        add_step(
            ACTION_STOP,
            explanation="Aucune règle applicable ne produit de nouveau fait : arrêt.",
        )
        return result(False, f"Objectif « {goal} » non démontré par chaînage avant.")
