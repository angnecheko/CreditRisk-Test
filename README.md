# CreditRisk-Test

Prototype FastAPI d'estimation du risque de défaut de remboursement.

## Démarrage local sous PowerShell

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m app.training
.venv/Scripts/python.exe -m uvicorn app.main:app
```

Le modèle local est entraîné sur 600 demandes synthétiques générées avec la
graine 42. La cible simulée dépend de la charge mensuelle de remboursement
rapportée au revenu et de l'ancienneté d'activité. Ce jeu sert à tester le
prototype. Il ne permet pas d'évaluer ses performances sur des crédits réels.
Le seuil de risque élevé est fixé à 0,5 pour ce prototype pédagogique.
Charger uniquement un artefact joblib produit par une source de confiance.

- `GET /health` indique si le modèle est disponible.
- `GET /model-info` donne la version et les variables attendues.
- `POST /predict` accepte une demande JSON et retourne une probabilité,
  un niveau de risque et la version du modèle.

Exemple de demande :

```json
{"age":35,"revenu_mensuel":250000,"montant_credit":1000000,"duree_mois":12,"anciennete_activite":4}
```

## Tests

```powershell
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m pytest --cov=app --cov-report=term-missing
```
