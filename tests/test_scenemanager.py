from typing import final, override

import pygame
import pytest

from client.scene import Scene, SceneManager

# Tests unitaires du SceneManager : pile de scènes (push/pop), propagation
# de la mise à jour (process) et transmission des arguments au constructeur
# des scènes.


class DummyScene(Scene):
    """Minimal concrete Scene that records lifecycle calls."""
    # Scène factice qui enregistre ses appels de cycle de vie pour pouvoir
    # les vérifier dans les assertions des tests.

    def __init__(self, *, propagate: bool = False) -> None:
        self.entered: bool = False
        self.exited: bool = False
        self.process_calls: list[float] = []
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


@final
class ArgScene(Scene):
    """Scene that accepts extra constructor arguments."""
    # Sert à vérifier que SceneManager.push() transmet bien les arguments
    # supplémentaires (*args, **kwargs) au constructeur de la scène

    def __init__(self, value: int, *, label: str = "default") -> None:
        self.value = value
        self.label = label
        super().__init__()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        return False


def test_initial_state():
    # Un SceneManager fraîchement créé doit être vide, sans scène courante
    sm = SceneManager()
    assert sm.empty is True
    assert sm.current is None


def test_push_returns_instance():
    # push() doit renvoyer l'instance de scène qu'il vient de créer
    sm = SceneManager()
    instance = sm.push(DummyScene)
    assert isinstance(instance, DummyScene)


def test_push_sets_current():
    # Après un push, la scène ajoutée doit devenir la scène "courante"
    sm = SceneManager()
    scene = sm.push(DummyScene)
    assert sm.current is scene
    assert sm.empty is False


def test_push_forwards_args_and_kwargs():
    # Les arguments passés à push() doivent être transmis au constructeur de la scène
    sm = SceneManager()
    scene = sm.push(ArgScene, 42, label="hello")
    assert scene.value == 42
    assert scene.label == "hello"


def test_push_stacks_scenes():
    # La dernière scène empilée devient la scène courante (comportement de pile)
    sm = SceneManager()
    sm.push(DummyScene)
    second = sm.push(DummyScene)
    assert sm.current is second


def test_pop_removes_top_scene():
    # pop() retire la scène du sommet ; la scène en dessous redevient courante
    sm = SceneManager()
    first = sm.push(DummyScene)
    sm.push(DummyScene)
    sm.pop()
    assert sm.current is first


def test_pop_calls_cleanup():
    # pop() doit appeler on_exit() sur la scène retirée
    sm = SceneManager()
    scene = sm.push(DummyScene)
    sm.pop()
    assert scene.exited is True


def test_pop_on_empty_is_noop():
    # pop() sur un manager déjà vide ne doit rien faire (et surtout ne pas planter)
    sm = SceneManager()
    sm.pop()  # should not raise
    assert sm.empty is True


def test_pop_all_makes_empty():
    # Dépiler toutes les scènes une par une doit vider entièrement le manager
    sm = SceneManager()
    sm.push(DummyScene)
    sm.push(DummyScene)
    sm.pop()
    sm.pop()
    assert sm.empty is True
    assert sm.current is None


def test_process_calls_scenes_in_order():
    # Si toutes les scènes propagent (renvoient True), toutes doivent être mises à jour
    sm = SceneManager()
    first = sm.push(DummyScene, propagate=True)
    second = sm.push(DummyScene, propagate=True)

    events = pygame.event.get()
    sm.process(0.016, events)

    assert first.process_calls == [0.016]
    assert second.process_calls == [0.016]


def test_process_stops_propagation_when_false():
    # La mise à jour part du sommet de la pile vers le bas ; dès qu'une scène
    # renvoie False, les scènes encore plus bas ne sont pas mises à jour du tout
    sm = SceneManager()
    first = sm.push(DummyScene, propagate=True)
    second = sm.push(DummyScene, propagate=False)
    third = sm.push(DummyScene, propagate=True)

    events = pygame.event.get()
    sm.process(0.5, events)

    assert third.process_calls == [0.5]
    assert second.process_calls == [0.5]
    assert first.process_calls == []


def test_process_propagates_through_all_when_all_true():
    # Avec 5 scènes qui propagent toutes, elles doivent toutes recevoir la mise à jour
    sm = SceneManager()
    scenes = [sm.push(DummyScene, propagate=True) for _ in range(5)]

    events = pygame.event.get()
    sm.process(1.0, events)

    for s in scenes:
        assert s.process_calls == [1.0]


def test_process_on_empty_manager_is_noop():
    # process() sur un manager vide ne doit pas planter
    sm = SceneManager()
    events = pygame.event.get()
    sm.process(0.016, events)  # should not raise


def test_push_pop_push_works():
    # Vérifie qu'on peut réutiliser le manager normalement après un cycle push/pop
    sm = SceneManager()
    sm.push(DummyScene)
    sm.pop()
    scene = sm.push(DummyScene)
    assert sm.current is scene
    assert sm.empty is False


def test_multiple_process_calls_accumulate():
    # Chaque appel à process() doit ajouter une nouvelle entrée à process_calls
    # (elles s'accumulent, elles ne remplacent pas la précédente)
    sm = SceneManager()
    scene = sm.push(DummyScene)
    events = pygame.event.get()
    sm.process(0.1, events)
    sm.process(0.2, events)
    sm.process(0.3, events)
    assert scene.process_calls == [0.1, 0.2, 0.3]


def test_process_dt_passed_correctly():
    # Vérifie que le delta-temps (dt) est transmis fidèlement à la scène
    sm = SceneManager()
    scene = sm.push(DummyScene)
    events = pygame.event.get()
    sm.process(0.033, events)
    assert scene.process_calls[-1] == pytest.approx(0.033)


def test_pop_does_not_affect_scenes_below():
    # Retirer la scène du sommet ne doit pas déclencher on_exit sur les scènes
    # restantes en dessous (elles ne sont pas concernées)
    sm = SceneManager()
    first = sm.push(DummyScene)
    sm.push(DummyScene)
    sm.pop()
    assert first.exited is False
    assert first.entered is True


def test_push_triggers_on_enter():
    # push() doit appeler on_enter() sur la nouvelle scène
    sm = SceneManager()
    scene = sm.push(DummyScene)
    assert scene.entered is True


def test_process_after_pop():
    # Une scène retirée (pop) ne doit plus jamais recevoir de mise à jour, même
    # si process() est appelé ensuite
    sm = SceneManager()
    first = sm.push(DummyScene, propagate=True)
    second = sm.push(DummyScene, propagate=True)
    sm.pop()
    events = pygame.event.get()
    sm.process(0.5, events)
    assert first.process_calls == [0.5]
    assert second.process_calls == []  # was popped, should not receive ticks


def test_single_scene_propagate_false():
    # Une seule scène qui ne propage pas doit quand même être mise à jour elle-même
    # (le "blocage de propagation" ne concerne que les scènes EN DESSOUS d'elle)
    sm = SceneManager()
    scene = sm.push(DummyScene, propagate=False)
    events = pygame.event.get()
    sm.process(0.1, events)
    assert scene.process_calls == [0.1]


def test_push_returns_correct_type():
    # Le type exact de l'instance renvoyée doit correspondre à la classe demandée
    sm = SceneManager()
    scene = sm.push(ArgScene, 10)
    assert type(scene) is ArgScene
