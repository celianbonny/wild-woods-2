from dataclasses import dataclass


@dataclass
class Targeting:
    """Composant ECS qui gère le ciblage d'une entité (ex: une tourelle visant un ennemi)."""

    range: float                      # Portée maximale de détection d'une cible
    distance: float = float("inf")    # Distance actuelle à la cible (infini = pas de cible à portée)
    target: int | None = None         # Identifiant de l'entité ciblée (None si aucune cible)
