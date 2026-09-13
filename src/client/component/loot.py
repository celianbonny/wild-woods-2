from dataclasses import dataclass, field
from enum import IntEnum, auto

# Composants ECS liés au butin (loot) et à l'inventaire.


class ItemKind(IntEnum):
    """Types d'objets ramassables dans le jeu."""
    HEALTH = auto()   # Objet de soin
    LIMBS = auto()    # Membres/pièces (ressource de craft ?)
    GOLD = auto()      # Monnaie du jeu


class LootTableKind(IntEnum):
    """Types de tables de butin, définissant combien d'objets peuvent tomber."""
    LOOT_ONE = auto()    # Fait tomber un seul objet
    LOOT_MANY = auto()   # Peut faire tomber plusieurs objets


@dataclass
class LootTable:
    """Table de butin associée à une entité (ex: un ennemi), définissant les objets
    qu'elle peut lâcher à sa mort et leurs probabilités."""
    kind: LootTableKind
    # Liste de paires (type d'objet, probabilité) définissant le butin possible
    entries: list[tuple[ItemKind, float]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ItemTag:
    """Marque une entité comme étant un objet ramassable au sol, avec son type."""
    kind: ItemKind


@dataclass
class Inventory:
    """Inventaire d'une entité (ex: le joueur), comptant le nombre de chaque objet."""
    counts: dict[ItemKind, int] = field(default_factory=dict)

    def add(self, kind: ItemKind, amount: int = 1) -> None:
        """Ajoute `amount` exemplaires de l'objet `kind` à l'inventaire."""
        self.counts[kind] = self.counts.get(kind, 0) + amount

    def count(self, kind: ItemKind) -> int:
        """Renvoie la quantité actuellement possédée de l'objet `kind` (0 si absent)."""
        return self.counts.get(kind, 0)
