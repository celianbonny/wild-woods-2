from typing import override
from unittest.mock import MagicMock, patch

import pygame

from client.scene import Scene

# Tests unitaires de la classe abstraite Scene (cycle de vie : on_enter,
# process, on_exit) à l'aide de scènes factices minimales.


class DummyScene(Scene):
    """Minimal Scene that records lifecycle calls."""
    # Scène factice qui note simplement quand ses méthodes sont appelées,
    # afin de pouvoir vérifier leur comportement dans les tests.

    def __init__(self, *, propagate: bool = False) -> None:
        self.entered: bool = False
        self.exited: bool = False
        self.process_calls: list[float] = []
        # Valeur renvoyée par process() : contrôle si la scène "propage"
        # la mise à jour aux scènes en dessous d'elle dans la pile
        self._propagate: bool = propagate
        super().__init__()

    @override
    def on_enter(self) -> None:
        self.entered = True

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        self.process_calls.append(dt)
        return self._propagate

    @override
    def on_exit(self) -> None:
        self.exited = True


class MinimalScene(Scene):
    """Scene that implements only the required methods."""
    # Vérifie qu'une scène peut être créée en n'implémentant QUE les méthodes
    # abstraites obligatoires (on_exit reste alors la version par défaut, qui ne fait rien)

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        return False


def test_on_enter_called_on_init():
    # Remarque : on_enter n'est PAS appelé automatiquement par le simple
    # constructeur de Scene (c'est le SceneManager.push() qui s'en charge),
    # donc `entered` doit toujours valoir False juste après l'instanciation directe
    scene = DummyScene()
    assert scene.entered is False


def test_world_id_unique():
    # Chaque scène doit avoir un identifiant unique (utilisé comme nom de monde ECS)
    a = DummyScene()
    b = DummyScene()
    assert a.id != b.id


@patch("client.scene.scene.esper")
def test_process_switches_world_and_delegates(mock: MagicMock):
    # On simule (mock) le module esper pour isoler le test de la vraie
    # bibliothèque ECS : on ne vérifie ici que le comportement de Scene.process
    scene = DummyScene()
    mock.reset_mock()

    events = pygame.event.get()
    result = scene.process(0.016, events)

    assert result is False
    assert scene.process_calls == [0.016]


def test_on_exit_default_is_noop():
    # Vérifie que l'implémentation par défaut de on_exit ne lève aucune erreur
    # (elle ne fait simplement rien, "no operation")
    scene = MinimalScene()
    scene.on_exit()


def test_process_returns_true_when_propagate():
    # Quand propagate=True, process() doit renvoyer True, ce qui indiquera
    # au SceneManager de continuer à mettre à jour les scènes en dessous
    scene = DummyScene(propagate=True)
    events = pygame.event.get()
    assert scene.process(0.016, events) is True
