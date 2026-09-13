# Point d'entrée du package "processor" : ré-expose tous les processeurs (systèmes ECS)
# du jeu pour un import simplifié depuis "client.processor".
from .animation import AnimationProc, DirectionalAnimationProc
from .brain import BrainProc
from .campfire import CampfireProc
from .collision import CollisionProc
from .damage import DamageProc
from .input import InputProc
from .lifetime import LifetimeProc
from .loot import LootProc
from .movement import MovementProc
from .pickup import PickupProc
from .render import RenderProc
from .shooting import ShootingProc
from .spatial_grid import SpatialGridProc
from .targeting import TargetingProc


__all__ = [
    "DirectionalAnimationProc",
    "AnimationProc",
    "BrainProc",
    "CampfireProc",
    "CollisionProc",
    "DamageProc",
    "InputProc",
    "LootProc",
    "MovementProc",
    "PickupProc",
    "RenderProc",
    "TargetingProc",
    "ShootingProc",
    "SpatialGridProc",
    "LifetimeProc",
]
