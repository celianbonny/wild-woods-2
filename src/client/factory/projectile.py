import esper
import pygame

from client.component import (
    DamageDealer,
    Lifetime,
    Position,
    ProjectileTag,
    Sprite,
    Velocity,
    Hitbox,
)

# Fabrique permettant de créer les entités "projectile" (tirées par une arme).


def create_projectile(pos: Position, vel: Velocity, damage: float):
    """Crée un projectile (petit disque noir) à la position `pos`, se déplaçant
    à la vitesse `vel` et infligeant `damage` points de dégâts au contact."""
    surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(surface, (0, 0, 0), (5, 5), 5)

    # Calcule le rectangle réellement occupé par les pixels dessinés (pas transparents)
    # afin d'avoir une hitbox ajustée au visuel plutôt qu'au carré complet de la surface
    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    esper.create_entity(
        Position(pos.x, pos.y),
        vel,
        Sprite(surface),
        ProjectileTag(),
        DamageDealer(amount=damage),
        Lifetime(time=8.0),  # Le projectile disparaît automatiquement après 8 secondes
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
    )
