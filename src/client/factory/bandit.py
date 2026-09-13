import esper
import pygame

from client.component import (
    AI,
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    DirectionalAnimation,
    DamageDealer,
    EnemyTag,
    Health,
    Hitbox,
    ItemKind,
    LootTable,
    LootTableKind,
    PatrolRuntime,
    PatrolSettings,
    Position,
    Speed,
    Sprite,
    Targeting,
    Velocity,
)

# Fabrique permettant de créer un ennemi ("bandit"/zombie) avec son IA,
# ses animations et sa table de butin.


def _load_sequence(path_template: str, count: int) -> list[pygame.Surface]:
    """Charge une séquence d'images numérotées de 1 à `count`."""
    return [
        pygame.image.load(path_template.format(i=i)).convert_alpha()
        for i in range(1, count + 1)
    ]


def create_bandit(pos: Position, difficulty: int = 0):
    """Crée un ennemi à la position `pos`. Le paramètre `difficulty` augmente
    sa vitesse et ses points de vie (utilisé pour faire progresser la difficulté)."""
    directions = ["up", "down", "left", "right"]
    dir_map = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
    }

    # Charge uniquement les animations de course (pas d'animation "idle" pour cet ennemi)
    clips: dict[str, AnimationClip] = {}
    for direction in directions:
        run_frames = _load_sequence(
            f"assets/sprite/ennemis/run/{dir_map[direction]}/{{i}}.png",
            9,
        )
        clips[f"run_{direction}"] = AnimationClip(
            frames=run_frames, frame_duration=0.08, loop=True
        )

    surface = clips["run_down"].frames[0]
    # Table de butin : peut potentiellement lâcher soin, membres et/ou or (indépendamment)
    entries = [
        (ItemKind.HEALTH, 0.1),
        (ItemKind.LIMBS, 0.1),
        (ItemKind.GOLD, 1.0),
    ]

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    esper.create_entity(
        pos,
        Velocity(0, 0),
        # Vitesse et PV augmentent avec le paramètre de difficulté
        Speed(200 + difficulty * 2),
        Health(10 + difficulty, 10 + difficulty),
        DamageDealer(amount=1.0),
        Sprite(surface),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
        EnemyTag(),
        AI(),
        Targeting(range=200),
        # Paramètres de patrouille aléatoires : rend chaque ennemi légèrement différent
        PatrolSettings.from_random(),
        PatrolRuntime(),
        LootTable(LootTableKind.LOOT_MANY, entries),
        AnimationSet(clips=clips),
        AnimationState(current="run_down"),
        AnimationRuntime(state="run_down", frame_index=0, frame_time=0.0),
        DirectionalAnimation(
            idle_prefix="idle",
            move_prefix="run",
            last_direction="down",
            speed_threshold=0.01,
        ),
    )
