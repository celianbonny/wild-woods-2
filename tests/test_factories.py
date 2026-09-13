import uuid

import esper
import pygame
import pytest

from client.component import (
    AI,
    EnemyTag,
    ItemKind,
    ItemTag,
    LootTable,
    PatrolRuntime,
    PatrolSettings,
    PlayerTag,
    Position,
    Speed,
    Sprite,
    Targeting,
    Velocity,
)
from client.factory import create_bandit, create_item, create_player

# Tests unitaires des fabriques (factories) : vérifie que les entités créées
# possèdent bien tous les composants attendus, avec les bonnes valeurs de départ.


@pytest.fixture
def esper_world():
    """Crée un monde ECS isolé et propre pour chaque test, puis le nettoie ensuite.

    Cela évite que les entités créées par un test n'interfèrent avec un autre test
    (chaque test démarre avec un monde vide)."""
    world_id = uuid.uuid4().hex
    esper.switch_world(world_id)
    yield world_id
    esper.switch_world("default")
    esper.delete_world(world_id)


class DummyImage:
    """Image factice remplaçant les vraies images pygame pendant les tests,
    pour ne pas dépendre de fichiers d'assets réels sur le disque."""
    def convert_alpha(self) -> pygame.Surface:
        return pygame.Surface((10, 10), pygame.SRCALPHA)


def test_create_player_adds_components(esper_world, monkeypatch):
    # Remplace le chargement d'image réel par notre image factice
    monkeypatch.setattr(pygame.image, "load", lambda _: DummyImage())

    create_player(Position(3, 4))

    # Vérifie qu'une seule entité joueur a été créée, avec les bons composants
    entities = list(esper.get_components(PlayerTag, Position, Velocity, Speed))
    assert len(entities) == 1
    ent, (tag, pos, vel, speed) = entities[0]
    sprite = esper.component_for_entity(ent, Sprite)

    assert isinstance(tag, PlayerTag)
    assert (pos.x, pos.y) == (3, 4)
    assert (vel.vx, vel.vy) == (0, 0)  # Le joueur démarre immobile
    assert speed.value == 300
    assert sprite.surface.get_size() == (10, 10)


def test_create_bandit_adds_components(esper_world, monkeypatch):
    monkeypatch.setattr(pygame.image, "load", lambda _: DummyImage())

    create_bandit(Position(5, 6))

    # Vérifie qu'un seul ennemi a été créé, avec tous ses composants de gameplay
    entities = list(esper.get_components(EnemyTag, Position, Velocity, Speed))
    assert len(entities) == 1
    ent_id, (tag, pos, vel, speed) = entities[0]

    sprite = esper.component_for_entity(ent_id, Sprite)
    ai = esper.component_for_entity(ent_id, AI)
    targeting = esper.component_for_entity(ent_id, Targeting)
    settings = esper.component_for_entity(ent_id, PatrolSettings)
    runtime = esper.component_for_entity(ent_id, PatrolRuntime)
    loot = esper.component_for_entity(ent_id, LootTable)

    assert isinstance(tag, EnemyTag)
    assert (pos.x, pos.y) == (5, 6)
    assert (vel.vx, vel.vy) == (0, 0)
    assert speed.value == 200  # Vitesse de base sans bonus de difficulté (difficulty=0)
    assert isinstance(sprite, Sprite)
    assert isinstance(ai, AI)
    assert targeting.range == 200
    assert isinstance(settings, PatrolSettings)
    assert isinstance(runtime, PatrolRuntime)
    assert len(loot.entries) == 3  # HEALTH, LIMBS, GOLD
