import math
from typing import final, override

import pygame
from esper import Processor

from client.view.player import PlayerView

# Processeur qui traduit les touches clavier pressées en vitesse de déplacement du joueur.


@final
class InputProc(Processor):
    @override
    def process(self, _):
        player = PlayerView.get()

        keys = pygame.key.get_pressed()
        # Réinitialise la vitesse avant de la recalculer à partir des touches pressées
        player.vel.vx = 0
        player.vel.vy = 0
        # Disposition clavier AZERTY : Z=haut, S=bas, Q=gauche, D=droite
        if keys[pygame.K_z]:
            player.vel.vy -= player.speed.value
        if keys[pygame.K_s]:
            player.vel.vy += player.speed.value
        if keys[pygame.K_q]:
            player.vel.vx -= player.speed.value
        if keys[pygame.K_d]:
            player.vel.vx += player.speed.value

        # Si l'on se déplace en diagonale, on normalise la vitesse (division par racine de 2)
        # pour éviter d'aller plus vite en diagonale qu'en ligne droite
        if player.vel.vx != 0 and player.vel.vy != 0:
            player.vel.vx /= math.sqrt(2)
            player.vel.vy /= math.sqrt(2)
