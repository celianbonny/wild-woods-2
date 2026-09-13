from dataclasses import dataclass

import pygame

# Composants ECS liés au rendu visuel et aux animations des entités.


@dataclass
class Sprite:
    """Image statique associée à une entité."""
    surface: pygame.Surface


@dataclass
class AnimationClip:
    """Une animation = une suite d'images (frames) jouées à une certaine vitesse."""
    frames: list[pygame.Surface]
    frame_duration: float   # Durée d'affichage de chaque frame (en secondes)
    loop: bool = True       # Si True, l'animation reboucle une fois terminée


@dataclass
class AnimationSet:
    """Ensemble nommé d'animations disponibles pour une entité (ex: "idle", "walk"...)."""
    clips: dict[str, AnimationClip]


@dataclass
class AnimationState:
    """Nom de l'animation actuellement demandée/sélectionnée pour l'entité."""
    current: str


@dataclass
class AnimationRuntime:
    """État d'exécution courant de l'animation en cours de lecture."""
    state: str          # Nom de l'animation en cours de lecture
    frame_index: int    # Index de la frame actuellement affichée
    frame_time: float   # Temps écoulé depuis l'affichage de la frame courante


@dataclass
class DirectionalAnimation:
    """Permet de choisir automatiquement l'animation à jouer selon la direction
    et la vitesse de déplacement de l'entité (ex: "walk_left", "idle_right"...)."""
    idle_prefix: str        # Préfixe des animations d'immobilité
    move_prefix: str        # Préfixe des animations de déplacement
    last_direction: str     # Dernière direction connue (pour garder l'orientation à l'arrêt)
    speed_threshold: float  # Vitesse minimale à partir de laquelle on considère que l'entité bouge


@dataclass
class Lifetime:
    """Durée de vie restante d'une entité avant sa suppression automatique."""
    time: float
