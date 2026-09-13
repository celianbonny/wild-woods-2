import uuid
from abc import ABC, abstractmethod
from typing import final

import esper
import pygame

# Classe de base abstraite "Scene" et gestionnaire de scènes "SceneManager".
#
# Le jeu est organisé comme une PILE (stack) de scènes : la scène du dessus
# (la dernière ajoutée) est celle qui est mise à jour et affichée en premier.
# Chaque scène possède aussi son propre "monde" ECS (esper), ce qui isole
# complètement les entités d'une scène par rapport aux autres (ex: le menu
# et la partie en cours n'ont pas les mêmes entités).


class Scene(ABC):
    def __init__(self) -> None:
        # Identifiant unique de la scène, utilisé comme nom de "monde" esper associé
        self._id: str = uuid.uuid4().hex

    @final
    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def on_enter(self) -> None:
        """Appelé une fois, quand la scène devient active (empilée)."""
        ...

    @abstractmethod
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        """Called every frame.

        Returns:
            True  — allow scenes below to process.
            False — stop propagation to scenes below.
        """
        ...

    def on_exit(self) -> None:
        """Appelé une fois, quand la scène est retirée de la pile (optionnel à redéfinir)."""
        ...


class SceneManager:
    """Gère la pile de scènes actives et leur cycle de vie."""

    def __init__(self) -> None:
        self._scenes: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        """Get the current active scene (the one on top of the stack)."""
        return self._scenes[-1] if self._scenes else None

    @property
    def empty(self) -> bool:
        """Check if there are no scenes in the stack."""
        return not self._scenes

    def push[T: Scene](self, scene: type[T], *args: object, **kwargs: object) -> T:
        """Push a new scene on top of the stack.

        Args:
            scene: The scene class to instantiate and push.
            *args, **kwargs: Arguments to pass to the scene constructor.

        Returns:
            The instance of the scene that was created and pushed.
        """
        instance = scene(*args, **kwargs)
        # Bascule sur le monde ECS dédié à cette scène avant d'appeler on_enter,
        # pour que les entités créées y soient correctement isolées
        esper.switch_world(instance.id)
        instance.on_enter()
        self._scenes.append(instance)
        return instance

    def pop(self) -> None:
        """Retire et détruit la scène du sommet de la pile (et son monde ECS associé)."""
        if not self._scenes:
            return
        scene = self._scenes[-1]
        esper.switch_world(scene.id)
        scene.on_exit()
        # Revient au monde "par défaut" avant de supprimer le monde de la scène,
        # car on ne peut pas supprimer le monde actuellement actif
        esper.switch_world("default")
        esper.delete_world(scene.id)
        self._scenes.pop()

    def process(self, dt: float, events: list[pygame.event.Event]) -> None:
        """Met à jour les scènes de la pile, de la plus haute (dernière ajoutée)
        vers la plus basse, en s'arrêtant dès qu'une scène renvoie False
        (ex: une scène de pause qui bloque la mise à jour de la scène de jeu
        en dessous)."""
        for scene in reversed(self._scenes):
            esper.switch_world(scene.id)
            if not scene.process(dt, events):
                break

    def clear(self) -> None:
        """Vide entièrement la pile de scènes (dépile jusqu'à ce qu'elle soit vide)."""
        while not self.empty:
            self.pop()
