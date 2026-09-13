from typing import final, override

import esper

from client.component import Lifetime

# Processeur qui gère la durée de vie limitée de certaines entités
# (par exemple des effets temporaires ou des projectiles qui doivent disparaître).


@final
class LifetimeProc(esper.Processor):
    @override
    def process(self, dt: float):
        expired: list[int] = []
        # On décrémente le temps restant de chaque entité possédant un composant Lifetime
        for ent, (life) in esper.get_component(Lifetime):
            life.time -= dt

            # Si le temps de vie est écoulé, on la marque pour suppression
            if life.time <= 0:
                expired.append(ent)

        # Suppression des entités expirées (fait après la boucle pour ne pas modifier
        # la liste d'entités pendant qu'on l'itère)
        for ent in expired:
            esper.delete_entity(ent)
