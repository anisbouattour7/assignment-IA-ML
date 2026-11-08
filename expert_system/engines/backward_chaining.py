from expert_system.engines.inference_engine import InferenceEngine
from expert_system.models.inference_result import InferenceResult
from expert_system.models.inference_step import (
    ACTION_APPLY_RULE,
    ACTION_CYCLE,
    ACTION_FACT_FOUND,
    ACTION_GOAL_KNOWN,
    ACTION_GOAL_REACHED,
    ACTION_NO_RULE,
    ACTION_RULE_FAILED,
    ACTION_STOP,
    ACTION_SUBGOAL,
    ACTION_TRY_RULE,
    InferenceStep,
)
from expert_system.models.knowledge_base import KnowledgeBase


class BackwardChaining(InferenceEngine):
    """Chaînage arrière : part de l'objectif et remonte vers les faits connus.

    Pour prouver un but, on cherche les règles qui le concluent (dans l'ordre de la base) ;
    chaque condition devient un sous-but à prouver récursivement. Une règle réussit si
    TOUS ses sous-buts sont prouvés. Les cycles sont évités grâce au chemin courant
    (la pile des buts en cours de démonstration).
    """

    method = "chaînage arrière"

    def infer(self, knowledge_base: KnowledgeBase, goal: str) -> InferenceResult:
        goal = goal.strip()
        initial = tuple(f.name for f in knowledge_base.get_facts())
        initial_set = set(initial)
        known = set(initial)  # copie de travail : faits initiaux + buts déjà démontrés
        derived: list[str] = []
        steps: list[InferenceStep] = []
        rules = knowledge_base.get_rules()

        def add_step(action: str, depth: int = 0, **kwargs) -> None:
            steps.append(InferenceStep(number=len(steps) + 1, action=action, depth=depth, **kwargs))

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

        def prove(current: str, depth: int, path: list[str]) -> bool:
            # 1) Déjà connu (fait initial ou but déjà démontré)
            if current in known:
                origin = "faits initiaux" if current in initial_set else "déjà démontré"
                add_step(
                    ACTION_FACT_FOUND,
                    depth,
                    derived_fact=current,
                    explanation=f"« {current} » est connu ({origin}).",
                )
                return True

            # 2) Cycle : ce but est déjà en cours de démonstration dans cette branche
            if current in path:
                add_step(
                    ACTION_CYCLE,
                    depth,
                    derived_fact=current,
                    explanation=f"Cycle sur « {current} » (déjà en cours de démonstration) : "
                    "branche abandonnée.",
                )
                return False

            # 3) Règles candidates : celles dont la conclusion est ce but
            candidates = [r for r in rules if r.conclusion == current]
            if not candidates:
                add_step(
                    ACTION_NO_RULE,
                    depth,
                    derived_fact=current,
                    explanation=f"« {current} » n'est pas un fait et aucune règle ne le "
                    "conclut : échec.",
                )
                return False

            add_step(
                ACTION_SUBGOAL,
                depth,
                derived_fact=current,
                explanation=f"Démontrer « {current} » : règle(s) candidate(s) "
                f"{', '.join(r.id for r in candidates)}.",
            )

            path.append(current)
            try:
                for rule in candidates:
                    add_step(
                        ACTION_TRY_RULE,
                        depth,
                        rule_id=rule.id,
                        matched_facts=rule.conditions,
                        derived_fact=current,
                        explanation=f"Essai de {rule.id} : il faut démontrer "
                        f"{' ET '.join(rule.conditions)}.",
                    )
                    failed = None
                    for condition in rule.conditions:
                        if not prove(condition, depth + 1, path):
                            failed = condition
                            break

                    if failed is None:
                        known.add(current)
                        derived.append(current)
                        add_step(
                            ACTION_APPLY_RULE,
                            depth,
                            rule_id=rule.id,
                            matched_facts=rule.conditions,
                            derived_fact=current,
                            explanation=f"{rule.id} vérifiée : "
                            f"{' ET '.join(rule.conditions)} ⇒ {current}.",
                        )
                        return True

                    add_step(
                        ACTION_RULE_FAILED,
                        depth,
                        rule_id=rule.id,
                        explanation=f"{rule.id} échoue : « {failed} » n'est pas démontrable.",
                    )
                return False
            finally:
                path.pop()

        # Cas particulier : objectif déjà présent dans les faits initiaux
        if goal in known:
            add_step(
                ACTION_GOAL_KNOWN,
                derived_fact=goal,
                explanation=f"« {goal} » figure déjà dans les faits initiaux : "
                "aucune règle nécessaire.",
            )
            return result(True, f"Objectif « {goal} » déjà présent dans la base de faits.")

        if prove(goal, 0, []):
            add_step(
                ACTION_GOAL_REACHED,
                derived_fact=goal,
                explanation=f"Objectif « {goal} » démontré.",
            )
            return result(
                True,
                f"Objectif « {goal} » démontré par chaînage arrière "
                f"({len(derived)} règle(s) utilisée(s)).",
            )

        add_step(
            ACTION_STOP,
            explanation="Aucune règle ne permet de démontrer l'objectif : arrêt.",
        )
        return result(False, f"Objectif « {goal} » non démontré par chaînage arrière.")
