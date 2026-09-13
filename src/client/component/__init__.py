# Point d'entrée du package "component" : ré-expose tous les composants ECS
# du jeu pour pouvoir écrire "from client.component import X" plutôt que
# de devoir connaître le sous-module exact de chaque composant.
from .ai import AI, AIState, PatrolRuntime, PatrolSettings
from .damage import DamageDealer, Health, Invincibility
from .gameplay import (
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    DirectionalAnimation,
    Lifetime,
    Sprite,
)
from .hitbox import Hitbox, aabb_overlap, hitbox_bounds
from .loot import Inventory, ItemKind, ItemTag, LootTable, LootTableKind
from .physics import Orientation, Position, Speed, Velocity
from .tags import CampfireTag, EnemyTag, PlayerTag, ProjectileTag
from .targeting import Targeting
from .weapon import Weapon

__all__ = [
    "AI",
    "AIState",
    "PatrolRuntime",
    "PatrolSettings",
    "Sprite",
    "AnimationClip",
    "AnimationSet",
    "AnimationState",
    "AnimationRuntime",
    "DirectionalAnimation",
    "Inventory",
    "ItemKind",
    "ItemTag",
    "LootTable",
    "LootTableKind",
    "Orientation",
    "Position",
    "Speed",
    "Velocity",
    "CampfireTag",
    "EnemyTag",
    "PlayerTag",
    "ProjectileTag",
    "Targeting",
    "Health",
    "DamageDealer",
    "Invincibility",
    "Weapon",
    "Lifetime",
    "Hitbox",
    "hitbox_bounds",
    "aabb_overlap",
]
