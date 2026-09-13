import math
from typing import final, override

import esper
import pygame

from client.component import Velocity
from client.factory.projectile import create_projectile
from client.view.player import PlayerView

# Processeur qui gère le tir du joueur avec la souris.


@final
class ShootingProc(esper.Processor):
    @override
    def process(self, dt: float):
        player = PlayerView.get()
        weapon = player.weapon()
        if weapon is None:
            # Le joueur n'a pas d'arme équipée : rien à faire
            return

        screen = pygame.display.get_surface()
        if screen is None:
            return

        # Décompte du temps de recharge (cooldown) de l'arme
        if weapon.cooldown_current > 0:
            weapon.cooldown_current -= dt

        # On ne tire que si le clic gauche est maintenu ET que l'arme n'est plus en recharge
        if not pygame.mouse.get_pressed()[0] or weapon.cooldown_current > 0:
            return

        width, height = screen.get_size()
        mpos_x, mpos_y = pygame.mouse.get_pos()

        # La caméra suit le joueur : le joueur est toujours affiché au centre de l'écran.
        # On convertit donc la position écran de la souris en position dans le monde.
        offset_x = width / 2 - player.pos.x
        offset_y = height / 2 - player.pos.y
        world_mouse_x = mpos_x - offset_x
        world_mouse_y = mpos_y - offset_y

        # Calcule l'angle entre le joueur et le curseur de la souris
        dx = world_mouse_x - player.pos.x
        dy = world_mouse_y - player.pos.y
        angle = math.atan2(dy, dx)

        # Déduit la vitesse (vecteur) du projectile à partir de cet angle
        vel_x = math.cos(angle) * weapon.bullet_speed
        vel_y = math.sin(angle) * weapon.bullet_speed

        create_projectile(player.pos, Velocity(vel_x, vel_y), weapon.damage)
        # Relance le temps de recharge de l'arme
        weapon.cooldown_current = weapon.cooldown_max
