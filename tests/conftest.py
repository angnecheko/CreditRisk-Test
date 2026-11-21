import joblib
import pytest
from fastapi.testclient import TestClient

from app.main import creer_app
from app.training import entrainer_reference


@pytest.fixture(scope="session", params=["1.0.0", "1.0.1"])
def version_modele(request):
    return request.param


@pytest.fixture(scope="session")
def chemin_modele(tmp_path_factory, version_modele):
    chemin = tmp_path_factory.mktemp("modele") / "model.joblib"
    regularisation = 1.0 if version_modele == "1.0.0" else 0.5
    joblib.dump(
        entrainer_reference(regularisation=regularisation, version=version_modele),
        chemin,
    )
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
