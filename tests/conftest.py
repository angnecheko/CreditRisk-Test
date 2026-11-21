import joblib
import pytest
from fastapi.testclient import TestClient

from app.main import creer_app
from app.training import entrainer_reference


@pytest.fixture(scope="session")
def chemin_modele(tmp_path_factory):
    chemin = tmp_path_factory.mktemp("modele") / "model.joblib"
    joblib.dump(entrainer_reference(), chemin)
    return chemin


@pytest.fixture
def client(chemin_modele):
    with TestClient(creer_app(chemin_modele)) as client:
        yield client


@pytest.fixture
def demande():
    return {
        "age": 35,
        "revenu_mensuel": 250000,
        "montant_credit": 1000000,
        "duree_mois": 12,
        "anciennete_activite": 4,
    }
