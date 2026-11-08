from dataclasses import dataclass


@dataclass(frozen=True)
class Fact:
    """Proposition atomique considérée vraie (identifiant textuel normalisé)."""

    name: str
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", self.name.strip())
        if not self.name:
            raise ValueError("Le nom d'un fait ne peut pas être vide.")

    def __str__(self) -> str:
        return self.name
