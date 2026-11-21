from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DemandeCredit(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)

    age: Annotated[int, Field(ge=18, le=100)]
    revenu_mensuel: Annotated[float, Field(gt=0, le=100_000_000)]
    montant_credit: Annotated[float, Field(gt=0, le=1_000_000_000)]
    duree_mois: Annotated[int, Field(ge=1, le=120)]
    anciennete_activite: Annotated[float, Field(ge=0, le=82)]
