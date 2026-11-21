import json

import pytest


@pytest.mark.parametrize("valeur", [float("inf"), float("-inf"), float("nan")])
def test_rejette_les_revenus_non_finis(client, demande, valeur):
    demande["revenu_mensuel"] = valeur
    reponse = client.post(
        "/predict",
        content=json.dumps(demande),
        headers={"content-type": "application/json"},
    )
    assert reponse.status_code == 422
    assert reponse.json() == {
        "detail": [{"loc": ["body", "revenu_mensuel"], "type": "finite_number"}]
    }


@pytest.mark.parametrize("age", [18, 100])
def test_accepte_les_bornes_de_l_age(client, demande, age):
    demande["age"] = age
    assert client.post("/predict", json=demande).status_code == 200


def test_rejette_un_tableau_json(client):
    reponse = client.post("/predict", json=[])
    assert reponse.status_code == 422
    assert reponse.json() == {
        "detail": [{"loc": ["body"], "type": "model_attributes_type"}]
    }


@pytest.mark.parametrize(
    "champ,valeur",
    [("montant_credit", 1_000_000_000), ("anciennete_activite", 82)],
    ids=["hors-distribution", "coherence-age-anciennete"],
)
def test_entrees_valides_selon_le_schema(client, demande, champ, valeur):
    demande[champ] = valeur
    reponse = client.post("/predict", json=demande)
    assert reponse.status_code == 200
    resultat = reponse.json()
    assert 0 <= resultat["probabilite_defaut"] <= 1
    assert set(resultat) == {"probabilite_defaut", "niveau_risque", "version_modele"}
