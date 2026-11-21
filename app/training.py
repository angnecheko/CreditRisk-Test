import argparse
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.preprocessing import VARIABLES

CHEMIN_MODELE = Path("model.joblib")


def entrainer_reference(*, regularisation: float = 1.0, version: str = "1.0.0"):
    rng = np.random.default_rng(42)
    taille = 600
    age = rng.integers(21, 66, taille)
    revenu = rng.integers(75_000, 750_001, taille)
    montant = rng.integers(100_000, 5_000_001, taille)
    duree = rng.integers(6, 37, taille)
    anciennete = rng.integers(0, 16, taille)
    variables = np.column_stack((age, revenu, montant, duree, anciennete))
    charge = montant / (duree * revenu)
    score = -1.5 + 3 * charge - 0.05 * anciennete
    defaut = rng.binomial(1, 1 / (1 + np.exp(-score)))
    modele = make_pipeline(StandardScaler(), LogisticRegression(C=regularisation))
    modele.fit(variables, defaut)
    return {"version": version, "variables": VARIABLES, "modele": modele}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=CHEMIN_MODELE)
    args = parser.parse_args()
    joblib.dump(entrainer_reference(), args.output)
