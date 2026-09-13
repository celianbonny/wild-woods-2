from dataclasses import dataclass

# Composants ECS de base liés à la physique/déplacement des entités.


@dataclass
class Position:
    """Position d'une entité dans le monde (coordonnées x, y)."""
    x: float
    y: float


@dataclass
class Velocity:
    """Vecteur vitesse d'une entité (déplacement par seconde sur x et y)."""
    vx: float
    vy: float


@dataclass
class Orientation:
    """Angle d'orientation d'une entité (en degrés ou radians selon l'usage)."""
    angle: float


@dataclass
class Speed:
    """Vitesse scalaire de déplacement d'une entité (norme du vecteur vitesse)."""
    value: float
