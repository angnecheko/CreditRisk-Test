import numpy as np

from app.validation import DemandeCredit

VARIABLES = tuple(DemandeCredit.model_fields)


def transformer(demande: DemandeCredit) -> np.ndarray:
    valeurs = demande.model_dump()
    return np.array([[valeurs[nom] for nom in VARIABLES]], dtype=float)
