import json

import pytest


@pytest.mark.parametrize("valeur", [float("inf"), float("-inf"), float("nan")])
def test_rejette_les_revenus_non_finis(client, demande, valeur):
    demande["revenu_mensuel"] = valeur
    reponse = client.post(
        "/predict", content=json.dumps(demande), headers={"content-type": "application/json"}
    )
    assert reponse.status_code == 422
    assert reponse.json() == {
        "detail": [{"loc": ["body", "revenu_mensuel"], "type": "finite_number"}]
    }


@pytest.mark.parametrize("age", [18, 100])
def test_accepte_les_bornes_de_l_age(client, demande, age):
    demande["age"] = age
    assert client.post("/predict", json=demande).status_code == 200
