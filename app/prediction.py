import math

from sklearn.pipeline import Pipeline

from app.preprocessing import transformer
from app.validation import DemandeCredit


def predire(modele: Pipeline, demande: DemandeCredit) -> float:
    indice_defaut = list(modele.classes_).index(1)
    probabilite = float(modele.predict_proba(transformer(demande))[0, indice_defaut])
    if not math.isfinite(probabilite) or not 0 <= probabilite <= 1:
        raise ValueError("Probabilité de défaut invalide")
    return probabilite
