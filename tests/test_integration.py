import joblib
import pytest

from app.preprocessing import VARIABLES


def test_pipeline_http(client, chemin_modele, demande):
    assert client.get("/health").json() == {"statut": "disponible"}
    infos = client.get("/model-info").json()
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
        ("app.main", "predire", "erreur"),
    ],
)
def test_erreur_interne_controlee(client, demande, monkeypatch, module, fonction, comportement):
    def defaillance(*_args):
        if comportement == "dimensions":
            return [[1.0]]
        raise ValueError("Détail technique interne")

    monkeypatch.setattr(f"{module}.{fonction}", defaillance)
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 500
    assert reponse.json() == {"detail": "Erreur de prédiction"}