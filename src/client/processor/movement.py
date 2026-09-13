from typing import final, override

import esper
from esper import Processor

from client.component import Position, Velocity

# Processeur de base qui applique le déplacement des entités selon leur vitesse.


@final
class MovementProc(Processor):
    @override
    def process(self, dt: float):
        # Pour chaque entité ayant une vitesse et une position,
        # on met à jour la position en fonction de la vitesse et du temps écoulé (dt)
        for _, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt
