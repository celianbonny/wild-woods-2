import random
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Self


class AIState(IntEnum):
    """États possibles de l'intelligence artificielle d'une entité (machine à états)."""
    IDLE = auto()      # L'entité ne fait rien, attend
    PATROL = auto()    # L'entité se déplace aléatoirement dans une zone
    CHASE = auto()      # L'entité poursuit une cible (ex: le joueur)
    ATTACK = auto()     # L'entité attaque sa cible
    DEAD = auto()        # L'entité est morte / désactivée


@dataclass
class AI:
    """Composant ECS portant l'état courant de l'IA d'une entité."""
    state: AIState = AIState.IDLE


@dataclass
class PatrolRuntime:
    """Données "en cours d'exécution" de la patrouille (mises à jour à chaque frame)."""
    timer: float = 0.0                          # Temps restant avant de changer de direction
    direction: tuple[float, float] = (0.0, 0.0)  # Direction de déplacement actuelle (vecteur normalisé)


@dataclass
class PatrolSettings:
    """Paramètres fixes définissant le comportement de patrouille d'une entité."""
    radius: float          # Rayon de la zone dans laquelle l'entité patrouille
    idle_chance: float     # Probabilité de rester immobile plutôt que de se déplacer
    min_time: float        # Durée minimale avant de changer de direction/état
    max_time: float        # Durée maximale avant de changer de direction/état

    @classmethod
    def from_random(cls) -> Self:
        """Génère des paramètres de patrouille aléatoires (pour varier le comportement
        des ennemis d'une entité à l'autre)."""
        return cls(
            radius=random.uniform(50, 200),
            idle_chance=random.uniform(0.1, 0.7),
            min_time=random.uniform(0.5, 1.0),
            max_time=random.uniform(1.5, 3.0),
        )
