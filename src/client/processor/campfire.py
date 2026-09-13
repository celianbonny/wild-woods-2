from typing import final, override

import esper
from esper import Processor

from client.component import AnimationState, CampfireTag, Health

# Processeur ECS chargé de gérer l'apparence visuelle des feux de camp
# en fonction de leurs points de vie restants.


@final
class CampfireProc(Processor):
    @override
    def process(self, dt: float) -> None:
        # Parcourt toutes les entités possédant à la fois un tag "feu de camp",
        # un composant de santé et un état d'animation
        for _, (_, health, anim_state) in esper.get_components(
            CampfireTag, Health, AnimationState
        ):
            # Si le feu a perdu plus de la moitié de ses PV, on bascule
            # sur l'animation "low-life" (feu faible), sinon animation normale
            target = "basic" if health.current / health.max > 0.5 else "low-life"
            if anim_state.current != target:
                anim_state.current = target
