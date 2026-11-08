from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    id: str
    conditions: list[str]
    conclusion: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", self.id.strip())
        object.__setattr__(self, "conditions", tuple(c.strip() for c in self.conditions))
        object.__setattr__(self, "conclusion", self.conclusion.strip())

    def is_applicable(self, facts: Collection[str]) -> bool:
        """Vrai si toutes les conditions sont présentes (une règle vide n'est jamais applicable)."""
        return bool(self.conditions) and all(c in facts for c in self.conditions)

    def __str__(self) -> str:
        return f"{self.id} : SI {' ET '.join(self.conditions)} ALORS {self.conclusion}"
