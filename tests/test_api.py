import math

import pytest
from fastapi.testclient import TestClient

from app.main import creer_app


def test_prediction_valide(client, demande, version_modele):
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 200
    resultat = reponse.json()
    assert set(resultat) == {"probabilite_defaut", "niveau_risque", "version_modele"}
    probabilite = resultat["probabilite_defaut"]
    assert math.isfinite(probabilite) and 0 <= probabilite <= 1
    assert resultat["niveau_risque"] == ("eleve" if probabilite >= 0.5 else "faible")
    assert resultat["version_modele"] == version_modele


@pytest.mark.parametrize(
    ("champ", "valeur", "type_erreur"),
    [
        ("age", -1, "greater_than_equal"),
        ("revenu_mensuel", "250000", "float_type"),
        ("montant_credit", 0, "greater_than"),
        ("montant_credit", -1, "greater_than"),
        ("duree_mois", 12.5, "int_type"),
        ("extra", True, "extra_forbidden"),
        ("montant_credit", 10**12, "less_than_equal"),
    ],
)
def test_entree_invalide(client, demande, champ, valeur, type_erreur):
    demande[champ] = valeur
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 422
    assert reponse.json() == {"detail": [{"loc": ["body", champ], "type": type_erreur}]}


def test_champ_manquant(client, demande):
    del demande["age"]
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 422
    assert reponse.json() == {"detail": [{"loc": ["body", "age"], "type": "missing"}]}


def test_json_mal_forme(client):
    reponse = client.post(
        "/predict", content="{", headers={"content-type": "application/json"}
    )
    assert reponse.status_code == 422
    assert reponse.json()["detail"][0]["type"] == "json_invalid"


def test_modele_indisponible(tmp_path, demande):
    with TestClient(creer_app(tmp_path / "absent.joblib")) as client:
        reponses = [
            client.get("/health"),
            client.get("/model-info"),
            client.post("/predict", json=demande),
        ]
    for reponse in reponses:
        assert reponse.status_code == 503
        assert reponse.json() == {"detail": "Modèle indisponible"}
