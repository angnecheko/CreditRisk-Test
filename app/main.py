from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sklearn.pipeline import Pipeline

from app.prediction import predire
from app.preprocessing import VARIABLES
from app.training import CHEMIN_MODELE
from app.validation import DemandeCredit


def creer_app(chemin_modele: Path = CHEMIN_MODELE) -> FastAPI:
    @asynccontextmanager
    async def lifespan(service: FastAPI):
        service.state.artefact = None
        try:
            artefact = joblib.load(chemin_modele)
            if (
                artefact["variables"] != VARIABLES
                or not isinstance(artefact["version"], str)
                or not isinstance(artefact["modele"], Pipeline)
            ):
                raise ValueError("Artefact incompatible")
            service.state.artefact = artefact
        except Exception:
            pass
        yield

    service = FastAPI(title="CreditRisk-Test", lifespan=lifespan)

    @service.exception_handler(RequestValidationError)
    async def erreur_validation(_requete: Request, erreur: RequestValidationError):
        details = [
            {"loc": element["loc"], "type": element["type"]}
            for element in erreur.errors()
        ]
        return JSONResponse(status_code=422, content={"detail": details})

    def artefact_disponible():
        if service.state.artefact is None:
            raise HTTPException(status_code=503, detail="Modèle indisponible")
        return service.state.artefact

    @service.get("/health")
    def health():
        artefact_disponible()
        return {"statut": "disponible"}

    @service.get("/model-info")
    def model_info():
        artefact = artefact_disponible()
        return {"version": artefact["version"], "variables": artefact["variables"]}

    @service.post("/predict")
    def predict(demande: DemandeCredit):
        artefact = artefact_disponible()
        try:
            probabilite = predire(artefact["modele"], demande)
        except Exception:
            raise HTTPException(status_code=500, detail="Erreur de prédiction") from None
        return {
            "probabilite_defaut": probabilite,
            "niveau_risque": "eleve" if probabilite >= 0.5 else "faible",
            "version_modele": artefact["version"],
        }

    return service


app = creer_app()
