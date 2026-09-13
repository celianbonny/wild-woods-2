from typing import final, override
import pygame
import esper
from esper import Processor

from client.component import (
    CampfireTag,
    Health,
    Hitbox,
    ItemKind,
    ItemTag,
    Position,
    aabb_overlap,
    hitbox_bounds,
)
from client.view.player import PlayerView

# Processeur qui gère le ramassage des objets au sol par le joueur.


@final
class PickupProc(Processor):
    def __init__(self):
        # Charge le son joué à chaque ramassage d'objet, avec un volume réduit
        self._coin_sound = pygame.mixer.Sound("assets/sound/pickup_coins.mp3")
        self._coin_sound.set_volume(0.2)

    @override
    def process(self, dt: float) -> None:
        items = esper.get_components(ItemTag, Position, Hitbox)
        if not items:
            return

        player = PlayerView.get()
        p_bounds = hitbox_bounds(player.pos, player.hitbox)

        picked: list[int] = []
        for item_ent, (item_tag, ipos, ihit) in items:
            # Ne ramasse l'objet que si sa hitbox chevauche celle du joueur
            if not aabb_overlap(p_bounds, hitbox_bounds(ipos, ihit)):
                continue

            player.inv.add(item_tag.kind)
            picked.append(item_ent)

            # Applique l'effet immédiat selon le type d'objet ramassé
            if item_tag.kind == ItemKind.HEALTH:
                # Objet de soin : rend 1 PV au joueur (sans dépasser son maximum)
                player.hp.current = min(player.hp.current + 1, player.hp.max)
            elif item_tag.kind == ItemKind.LIMBS:
                # Objet "membres" : soigne le feu de camp (s'il en existe un)
                campfires = esper.get_components(CampfireTag, Health)
                if campfires:
                    _, (_, chp) = campfires[0]
                    chp.current = min(chp.current + 1, chp.max)

        # Supprime les objets ramassés du monde (ils ont été transférés dans l'inventaire)
        for item_ent in picked:
            esper.delete_entity(item_ent)
