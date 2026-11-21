import os

import joblib
import pytest

from app.prediction import predire
from app.training import entrainer_reference
from app.validation import DemandeCredit


def test_probabilite_apres_rechargement(tmp_path, demande):
    artefact = entrainer_reference()
    entree = DemandeCredit.model_validate(demande)
    attendue = predire(artefact["modele"], entree)
    chemin = tmp_path / "model.joblib"
    joblib.dump(artefact, chemin)
    recharge = joblib.load(chemin)
    assert predire(recharge["modele"], entree) == pytest.approx(attendue, abs=1e-12, rel=0)


@pytest.mark.skipif(
    os.environ.get("CREDITRISK_ECHEC_VOLONTAIRE") != "1",
    reason="Scénario dédié à la vérification de la CI",
)
def test_echec_volontaire():
    assert False, "Échec volontaire demandé pour vérifier la CI"
