import esper
import pygame

from client.component import (
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    CampfireTag,
    Health,
    Hitbox,
    Position,
    Sprite,
    Invincibility,
)

# Fabrique permettant de créer un feu de camp (point stratégique à défendre).


def create_campfire(pos: Position, max_health: float = 10.0) -> None:
    """Crée une entité feu de camp à la position `pos`, avec `max_health` points de vie."""
    # Charge les frames d'animation "feu normal"
    basic_frames = [
        pygame.image.load(f"assets/sprite/campfire/basic/frame{i}.png").convert_alpha()
        for i in range(1, 6)
    ]
    # Charge les frames d'animation "feu faible" (peu de PV restants)
    low_frames = [
        pygame.image.load(
            f"assets/sprite/campfire/low-life/fire-low{i}.png"
        ).convert_alpha()
        for i in range(1, 4)
    ]
    clips = {
        "basic": AnimationClip(frames=basic_frames, frame_duration=0.15, loop=True),
        "low-life": AnimationClip(frames=low_frames, frame_duration=0.15, loop=True),
    }
    surface = basic_frames[0]
    # Rectangle réellement occupé par les pixels visibles (hors transparence)
    true_rect = surface.get_bounding_rect()
    esper.create_entity(
        pos,
        Sprite(surface),
        AnimationSet(clips=clips),
        AnimationState(current="basic"),
        AnimationRuntime(state="basic", frame_index=0, frame_time=0.0),
        Health(max=max_health, current=max_health),
        # La hitbox est plus petite que le sprite (on retire 160px de hauteur et on
        # décale de 80px vers le bas) pour ne bloquer que la base du feu, pas les flammes
        Hitbox(
            width=true_rect.width,
            height=true_rect.height - 160,
            offset_x=(true_rect.x + true_rect.width / 2) - surface.get_width() / 2,
            offset_y=80
            + (true_rect.y + true_rect.height / 2)
            - surface.get_height() / 2,
        ),
        CampfireTag(),
        Invincibility(0),
    )
