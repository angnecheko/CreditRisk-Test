import joblib
import pytest
from fastapi.testclient import TestClient

from app.main import creer_app

from app.preprocessing import VARIABLES


def test_pipeline_http(client, chemin_modele, demande):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"statut": "disponible"}
    model_info = client.get("/model-info")
    assert model_info.status_code == 200
    infos = model_info.json()
    assert infos["variables"] == list(VARIABLES)

    artefact = joblib.load(chemin_modele)
    donnees = [[demande[variable] for variable in VARIABLES]]
    attendue = artefact["modele"].predict_proba(donnees)[0, 1]
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 200
    assert reponse.json()["probabilite_defaut"] == pytest.approx(attendue)
    assert reponse.json()["version_modele"] == infos["version"] == artefact["version"]


@pytest.mark.parametrize(
    ("module", "fonction", "comportement"),
    [
        ("app.prediction", "transformer", "erreur"),
        ("app.prediction", "transformer", "dimensions"),
        ("app.prediction", "transformer", "variable_absente"),
        ("app.main", "predire", "erreur"),
    ],
)
def test_erreur_interne_controlee(
    client, demande, monkeypatch, module, fonction, comportement
):
    def defaillance(*_args):
        if comportement == "dimensions":
            return [[1.0]]
        if comportement == "variable_absente":
            raise KeyError("revenu_mensuel")
        raise ValueError("Détail technique interne")

    monkeypatch.setattr(f"{module}.{fonction}", defaillance)
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 500
    assert reponse.json() == {"detail": "Erreur de prédiction"}


def test_artefact_incompatible(tmp_path, chemin_modele, demande):
    artefact = joblib.load(chemin_modele)
    artefact["variables"] = artefact["variables"][1:]
    chemin = tmp_path / "incompatible.joblib"
    joblib.dump(artefact, chemin)
    with TestClient(creer_app(chemin)) as client:
        reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 503
    assert reponse.json() == {"detail": "Modèle indisponible"}
