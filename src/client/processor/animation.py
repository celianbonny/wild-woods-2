from typing import final, override

import esper
from esper import Processor

from client.component import (
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    DirectionalAnimation,
    Sprite,
    Velocity,
)

# Processeurs gérant les animations : choix de l'animation selon la direction
# de déplacement, puis lecture (défilement des frames) de l'animation choisie.


@final
class DirectionalAnimationProc(Processor):
    @override
    def process(self, dt: float) -> None:
        # Pour chaque entité orientable (ex: joueur, ennemis) : choisit l'animation
        # à jouer ("marche" ou "idle") selon sa direction/vitesse actuelle
        for _, (vel, direction, state) in esper.get_components(
            Velocity, DirectionalAnimation, AnimationState
        ):
            # Ne pas changer l'animation si l'entité est en train de mourir
            if state.current.startswith("death"):
                continue
            moving = (
                abs(vel.vx) > direction.speed_threshold
                or abs(vel.vy) > direction.speed_threshold
            )
            if moving:
                # Détermine la direction dominante (horizontale ou verticale)
                if abs(vel.vx) >= abs(vel.vy):
                    direction.last_direction = "right" if vel.vx > 0 else "left"
                else:
                    direction.last_direction = "down" if vel.vy > 0 else "up"
                state.current = f"{direction.move_prefix}_{direction.last_direction}"
            else:
                # À l'arrêt, on garde la dernière direction connue pour l'animation idle
                state.current = f"{direction.idle_prefix}_{direction.last_direction}"


@final
class AnimationProc(Processor):
    @override
    def process(self, dt: float) -> None:
        # Pour chaque entité animée, fait avancer la lecture de l'animation en cours
        for _, (sprite, anim_set, anim_state, runtime) in esper.get_components(
            Sprite, AnimationSet, AnimationState, AnimationRuntime
        ):
            # Si l'animation demandée a changé, on redémarre depuis la première frame
            if runtime.state != anim_state.current:
                runtime.state = anim_state.current
                runtime.frame_index = 0
                runtime.frame_time = 0.0

            clip = anim_set.clips.get(anim_state.current)
            if clip is None or not clip.frames:
                # Animation inconnue ou sans frame : rien à afficher
                continue

            runtime.frame_time += dt
            if runtime.frame_time >= clip.frame_duration:
                # Calcule combien de frames se sont écoulées (utile si dt est grand,
                # ex: lag, pour ne pas "perdre" des frames)
                steps = int(runtime.frame_time / clip.frame_duration)
                runtime.frame_time -= steps * clip.frame_duration
                if clip.loop:
                    # Animation bouclée : on revient au début après la dernière frame
                    runtime.frame_index = (runtime.frame_index + steps) % len(
                        clip.frames
                    )
                else:
                    # Animation non bouclée : on reste bloqué sur la dernière frame
                    runtime.frame_index = min(
                        runtime.frame_index + steps, len(clip.frames) - 1
                    )

            # Met à jour l'image affichée avec la frame courante de l'animation
            sprite.surface = clip.frames[runtime.frame_index]
