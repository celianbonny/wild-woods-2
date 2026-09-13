import esper
import pygame

from client.core import Engine, EngineEvent, StopCode
from client.scene import SceneManager

# Tests unitaires du moteur (Engine) : vérifie l'arrêt du moteur et la gestion
# de l'événement de fermeture de fenêtre (QUIT).


def test_engine_stop_sets_code(monkeypatch):
    # On remplace (mock) les fonctions pygame qui nécessiteraient un vrai
    # environnement graphique, pour pouvoir tester sans écran réel
    monkeypatch.setattr(pygame, "init", lambda: None)
    monkeypatch.setattr(pygame.display, "set_mode", lambda *_: pygame.Surface((10, 10)))
    monkeypatch.setattr(esper, "set_handler", lambda *_: None)

    Engine._scene_manager = SceneManager()
    engine = Engine()

    # Demande l'arrêt du moteur avec un code d'erreur
    engine.stop(code=StopCode.ERROR)

    # Le moteur doit se signaler comme arrêté, et run() doit renvoyer
    # immédiatement le code d'arrêt fourni (la boucle ne tourne plus)
    assert engine.is_running is False
    assert engine.run() == StopCode.ERROR


def test_engine_run_handles_quit(monkeypatch):
    monkeypatch.setattr(pygame, "init", lambda: None)
    monkeypatch.setattr(pygame.display, "set_mode", lambda *_: pygame.Surface((10, 10)))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    called = {}

    def fake_set_handler(event, handler):
        # Capture quel gestionnaire a été enregistré pour quel événement,
        # afin de vérifier que le moteur relie bien EngineEvent.STOP à self.stop
        called["event"] = event
        called["handler"] = handler

    monkeypatch.setattr(esper, "set_handler", fake_set_handler)

    # Simule un unique événement de fermeture de fenêtre (clic sur la croix)
    quit_event = pygame.event.Event(pygame.QUIT)
    monkeypatch.setattr(pygame.event, "get", lambda: [quit_event])

    Engine._scene_manager = SceneManager()
    engine = Engine()

    # Vérifie que le moteur a bien enregistré self.stop comme gestionnaire de STOP
    assert called["event"] == EngineEvent.STOP
    assert called["handler"] == engine.stop

    # La boucle doit se terminer immédiatement (dès le premier tour) car l'événement
    # QUIT déclenche l'arrêt, avec un code de sortie normal
    assert engine.run() == StopCode.NORMAL
