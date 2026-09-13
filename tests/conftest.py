# tests/conftest.py
from unittest.mock import patch
import pytest

# Configuration partagée par tous les tests (fixtures pytest automatiques).


@pytest.fixture(autouse=True)
def mock_pygame_events():
    """Simule l'absence d'événements clavier/souris pendant les tests.

    "autouse=True" signifie que cette fixture s'applique automatiquement
    à TOUS les tests du dossier, sans avoir besoin de la demander explicitement.
    Cela évite que les tests dépendent d'événements pygame réels (souris/clavier),
    ce qui les rendrait instables (flaky) ou impossibles à exécuter sans interface.
    """
    with patch("pygame.event.get", return_value=[]):
        yield
