import random
from typing import final, override

import esper
import pygame

from client.component import LootTable, LootTableKind, Position
from client.factory import create_item

# Processeur qui fait apparaître du butin au sol (touche de debug/test : "L")


@final
class LootProc(esper.Processor):
    @override
    def process(self, dt: float):
        # Ne déclenche le butin que sur un appui (unique, pas maintenu) de la touche L
        if not pygame.key.get_just_pressed()[pygame.K_l]:
            return
        for _, (loot, pos) in esper.get_components(LootTable, Position):
            if loot.kind == LootTableKind.LOOT_ONE:
                # Table "un seul objet" : on tire un objet au hasard parmi les entrées
                num = len(loot.entries)
                if num == 0:
                    continue
                idx = random.randint(0, num - 1)
                kind, _ = loot.entries[idx]
                create_item(Position(pos.x, pos.y), kind)
            elif loot.kind == LootTableKind.LOOT_MANY:
                # Table "plusieurs objets" : chaque entrée a sa propre probabilité
                # indépendante de tomber (peut donc faire apparaître 0, 1 ou plusieurs objets)
                for kind, chance in loot.entries:
                    if random.random() < chance:
                        create_item(Position(pos.x, pos.y), kind)
