from dataclasses import dataclass

from .physics import Position


@dataclass
class Hitbox:
    """Composant ECS représentant une zone de collision rectangulaire."""

    width: float
    height: float

    # Décalage du centre de la hitbox par rapport à la position de l'entité
    # (utile si le point d'ancrage du sprite n'est pas son centre)
    offset_x: float = 0.0
    offset_y: float = 0.0


def hitbox_bounds(pos: Position, hit: Hitbox) -> tuple[float, float, float, float]:
    """Calcule le rectangle englobant (AABB) d'une hitbox dans le monde,
    sous la forme (x_min, y_min, x_max, y_max)."""
    cx = pos.x + hit.offset_x
    cy = pos.y + hit.offset_y
    return (
        cx - hit.width / 2,
        cy - hit.height / 2,
        cx + hit.width / 2,
        cy + hit.height / 2,
    )


def aabb_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    """Teste si deux rectangles englobants (AABB) se chevauchent."""
    # Deux rectangles se chevauchent si leurs projections se recouvrent
    # à la fois sur l'axe X et sur l'axe Y
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
