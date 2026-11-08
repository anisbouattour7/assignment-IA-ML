import json
from pathlib import Path

from expert_system.models.fact import Fact
from expert_system.models.rule import Rule


class KnowledgeBaseError(ValueError):
    """Erreur de validation de la base de connaissances."""


class KnowledgeBase:
    """Faits initiaux + règles. Les dict conservent l'ordre d'insertion (ordre stable)."""

    def __init__(self) -> None:
        self._facts: dict[str, Fact] = {}
        self._rules: dict[str, Rule] = {}

    # ---------- faits ----------
    def add_fact(self, fact: Fact | str) -> bool:
        """Ajoute un fait. Retourne False si déjà présent (doublon ignoré)."""
        if isinstance(fact, str):
            fact = Fact(fact)
        if fact.name in self._facts:
            return False
        self._facts[fact.name] = fact
        return True

    def remove_fact(self, name: str) -> None:
        if name not in self._facts:
            raise KnowledgeBaseError(f"Fait inconnu : « {name} ».")
        del self._facts[name]

    def get_facts(self) -> list[Fact]:
        return list(self._facts.values())

    def fact_names(self) -> set[str]:
        return set(self._facts)

    # ---------- règles ----------
    def add_rule(self, rule: Rule) -> None:
        errors = self._rule_errors(rule)
        if errors:
            raise KnowledgeBaseError(" ; ".join(errors))
        self._rules[rule.id] = rule

    def remove_rule(self, rule_id: str) -> None:
        if rule_id not in self._rules:
            raise KnowledgeBaseError(f"Règle inconnue : « {rule_id} ».")
        del self._rules[rule_id]

    # partie update
    def update_fact(self, old_name: str, new_name: str) -> None:
        """Renomme un fait (l'ordre est conservé)."""
        if old_name not in self._facts:
            raise KnowledgeBaseError(f"Fait inconnu : « {old_name} ».")
        new_fact = Fact(new_name, self._facts[old_name].description)
        if new_fact.name != old_name and new_fact.name in self._facts:
            raise KnowledgeBaseError(f"Le fait « {new_fact.name} » existe déjà.")
        self._facts = {
            (new_fact.name if name == old_name else name): (new_fact if name == old_name else fact)
            for name, fact in self._facts.items()
        }

    def update_rule(self, old_id: str, rule: Rule) -> None:
        """Remplace une règle (l'ordre est conservé ; l'identifiant peut changer)."""
        if old_id not in self._rules:
            raise KnowledgeBaseError(f"Règle inconnue : « {old_id} ».")
        errors = self._rule_errors(rule, check_duplicate_id=False)
        if rule.id != old_id and rule.id in self._rules:
            errors.append(f"L'identifiant de règle « {rule.id} » existe déjà")
        if errors:
            raise KnowledgeBaseError(" ; ".join(errors))
        self._rules = {
            (rule.id if rid == old_id else rid): (rule if rid == old_id else existing)
            for rid, existing in self._rules.items()
        }

    def get_rules(self) -> list[Rule]:
        return list(self._rules.values())

    # ---------- utilitaires ----------
    def known_symbols(self) -> list[str]:
        """Tous les faits, conditions et conclusions connus (pour choisir un objectif)."""
        symbols = set(self._facts)
        for rule in self._rules.values():
            symbols.update(rule.conditions)
            symbols.add(rule.conclusion)
        return sorted(symbols)

    def validate(self) -> list[str]:
        """Retourne la liste des erreurs de cohérence (vide si tout est correct)."""
        errors: list[str] = []
        for rule in self._rules.values():
            errors += self._rule_errors(rule, check_duplicate_id=False)
        return errors

    def _rule_errors(self, rule: Rule, *, check_duplicate_id: bool = True) -> list[str]:
        errors: list[str] = []
        if not rule.id:
            errors.append("L'identifiant de la règle est vide")
        elif check_duplicate_id and rule.id in self._rules:
            errors.append(f"L'identifiant de règle « {rule.id} » existe déjà")
        if not rule.conditions:
            errors.append(f"{rule.id or '?'} : au moins une condition est requise")
        elif any(not c for c in rule.conditions):
            errors.append(f"{rule.id or '?'} : une condition est vide")
        if not rule.conclusion:
            errors.append(f"{rule.id or '?'} : la conclusion est vide")
        return errors

    # ---------- persistance JSON ----------
    def to_dict(self) -> dict:
        return {
            "facts": [f.name for f in self._facts.values()],
            "rules": [
                {"id": r.id, "conditions": list(r.conditions), "conclusion": r.conclusion}
                for r in self._rules.values()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBase":
        kb = cls()
        try:
            for name in data.get("facts", []):
                kb.add_fact(name)
            for r in data.get("rules", []):
                kb.add_rule(Rule(r["id"], r["conditions"], r["conclusion"]))
        except (KeyError, TypeError, AttributeError) as exc:
            raise KnowledgeBaseError(f"Format de base de connaissances invalide : {exc!r}") from exc
        return kb

    @classmethod
    def load_json(cls, path: str | Path) -> "KnowledgeBase":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save_json(self, path: str | Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
