import random
from typing import Callable, final, override

import esper
import pygame

from client.component import (
    AnimationState,
    CampfireTag,
    EnemyTag,
    Health,
    LootTable,
    LootTableKind,
    PlayerTag,
    Position,
    Speed,
    Sprite,
    Weapon,
)
from client.factory import create_item

# Processeur qui gère la mort des entités : joueur (fin de partie), ennemis (butin,
# suppression) et feu de camp (état "détruit").


@final
class DeathProc(esper.Processor):
    def __init__(self, on_game_over: Callable[[], None]):
        super().__init__()
        self._on_game_over = on_game_over  # Callback appelé quand la partie est perdue

        self.death_timer = 2.0             # Délai (secondes) avant de déclencher le game over
        self._game_over_signaled = False   # Empêche de signaler le game over plusieurs fois

        # Image de secours affichée si le joueur meurt mais n'a pas d'animation de mort
        self.dead_image = pygame.image.load(
            "assets/sprite/player/hurt/up/6.png"
        ).convert_alpha()

    @override
    def process(self, dt: float):
        if self._game_over_signaled:
            # Le game over a déjà été déclenché, plus rien à faire ici
            return
        p_ent, (_, php, pspeed, psprite) = esper.get_components(
            PlayerTag, Health, Speed, Sprite
        )[0]

        if php.current <= 0:
            # Le joueur est mort : on fige ses PV à 0, on l'immobilise
            php.current = 0
            pspeed.value = 0
            if esper.has_component(p_ent, Weapon):
                # On lui retire son arme pour qu'il ne puisse plus tirer une fois mort
                esper.remove_component(p_ent, Weapon)

            try:
                anim_state = esper.component_for_entity(p_ent, AnimationState)
            except KeyError:
                anim_state = None

            if anim_state is not None:
                # Joue l'animation de mort si le joueur en possède une
                anim_state.current = "death_up"
            else:
                # Sinon, affiche simplement l'image de secours
                psprite.surface = self.dead_image

            # Décompte le délai avant l'affichage de l'écran de game over
            # (laisse le temps à l'animation de mort de se jouer)
            self.death_timer -= dt

            if self.death_timer <= 0:
                self._on_game_over()
                self._game_over_signaled = True

        # Traite la mort des ennemis : suppression + génération éventuelle de butin
        dead_enemies: list[int] = []
        for e_ent, (_, ehp, _) in esper.get_components(EnemyTag, Health, Sprite):
            if ehp.current <= 0:
                ehp.current = 0
                dead_enemies.append(e_ent)

                if not esper.has_component(e_ent, LootTable):
                    continue

                loot = esper.component_for_entity(e_ent, LootTable)
                pos = esper.component_for_entity(e_ent, Position)

                if loot.kind == LootTableKind.LOOT_ONE:
                    # Fait tomber un seul objet, tiré au hasard parmi la table de butin
                    num = len(loot.entries)
                    if num == 0:
                        continue
                    idx = random.randint(0, num - 1)
                    kind, _ = loot.entries[idx]
                    create_item(Position(pos.x, pos.y), kind)
                elif loot.kind == LootTableKind.LOOT_MANY:
                    # Chaque type d'objet a sa propre chance indépendante de tomber
                    for kind, chance in loot.entries:
                        if random.random() < chance:
                            create_item(Position(pos.x, pos.y), kind)

        # Supprime définitivement les ennemis morts, une fois le butin généré
        for e_ent in dead_enemies:
            esper.delete_entity(e_ent)

        # Fige les PV du feu de camp à 0 s'il est détruit
        # (la logique de fin de partie liée au feu de camp est gérée ailleurs)
        campfire = esper.get_components(CampfireTag, Health)
        if not campfire:
            return
        _, (_, chp) = campfire[0]
        if chp.current <= 0:
            chp.current = 0
