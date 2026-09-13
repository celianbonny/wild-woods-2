from enum import IntEnum, auto
from typing import cast, final

import esper
import pygame

from client.scene import SceneManager

from .event import EngineEvent

# Le moteur du jeu : initialise pygame, gère la fenêtre, la boucle principale
# et un mode "debug" permettant de mettre le jeu en pause / avancer image par image.


class StopCode(IntEnum):
    """Code de sortie renvoyé par le moteur à la fin de son exécution."""
    NORMAL = 0
    ERROR = auto()


@final
class Engine:
    def __init__(self):
        pygame.init()
        # Ouvre une fenêtre en plein écran avec double buffering (évite le scintillement)
        self._screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF
        )
        # Enregistre self.stop comme gestionnaire de l'événement "STOP" du moteur ECS,
        # ce qui permet à n'importe quel processeur de demander l'arrêt du jeu
        esper.set_handler(EngineEvent.STOP, self.stop)
        self._scene_manager = SceneManager()
        self._clock = pygame.time.Clock()
        self._is_running = True
        self._stop_code = StopCode.NORMAL
        # État du mode debug (activable/désactivable en jeu)
        self._debug_enabled = False
        self._debug_paused = False
        self._debug_step_requested = False
        self._debug_step_dt = 1 / 60  # Pas de temps utilisé pour avancer d'une frame en debug

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def sm(self) -> SceneManager:
        """Accès au gestionnaire de scènes."""
        return self._scene_manager

    @property
    def screen(self) -> pygame.Surface:
        """Accès à la surface d'affichage principale (la fenêtre)."""
        return self._screen

    @property
    def debug_enabled(self) -> bool:
        return self._debug_enabled

    @property
    def debug_paused(self) -> bool:
        return self._debug_paused

    @property
    def debug_step_dt(self) -> float:
        return self._debug_step_dt

    def stop(self, *, code: StopCode = StopCode.NORMAL):
        """Arrête proprement la boucle principale du jeu."""
        self._is_running = False
        self._stop_code = code

    def _handle_engine_keys(self, events: list[pygame.event.Event]) -> None:
        """Gère les touches globales du moteur (fermeture de fenêtre, mode debug)."""
        for event in events:
            if event.type == pygame.QUIT:
                # Clic sur la croix de fermeture de la fenêtre
                self.stop()
                continue
            if event.type != pygame.KEYDOWN:
                continue

            key = cast(int, event.key)
            if key == pygame.K_RSHIFT:
                # Active/désactive le mode debug
                self._debug_enabled = not self._debug_enabled
                if not self._debug_enabled:
                    self._debug_paused = False
                self._debug_step_requested = False
            elif key == pygame.K_RCTRL and self._debug_enabled:
                # Met en pause / reprend la simulation (uniquement en mode debug)
                self._debug_paused = not self._debug_paused
                self._debug_step_requested = False
            elif key == pygame.K_RIGHT and self._debug_enabled and self._debug_paused:
                # Demande d'avancer d'une seule frame pendant la pause
                self._debug_step_requested = True

    def _resolve_dt(self, dt: float) -> float:
        """Calcule le delta-temps réel à utiliser pour cette frame, en tenant
        compte de la pause debug (dt=0 si en pause, sauf pas-à-pas demandé)."""
        if not (self._debug_enabled and self._debug_paused):
            return dt
        if self._debug_step_requested:
            self._debug_step_requested = False
            return self._debug_step_dt
        return 0.0

    def run(self) -> StopCode:
        """Boucle principale du jeu : tourne jusqu'à ce que self._is_running soit False."""
        while self._is_running:
            # Temps écoulé depuis la dernière frame (en secondes)
            dt = self._clock.tick() / 1000
            events = pygame.event.get()
            self._handle_engine_keys(events)
            dt = self._resolve_dt(dt)
            # Met à jour et affiche la scène courante
            self._scene_manager.process(dt, events)
            pygame.display.flip()
        return self._stop_code
