## 8. Exécution locale sous PowerShell

Exécuter ces commandes depuis la racine du dépôt. Si nécessaire, cloner d’abord le dépôt avec un compte GitHub qui dispose de l’accès.

```powershell
git clone https://github.com/angnecheko/CreditRisk-Test.git
Set-Location CreditRisk-Test
```

### Préparer Python et entraîner le modèle

Le projet utilise Python 3.13. La commande d’entraînement écrit l’artefact local `model.joblib`.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.training
```

### Lancer et interroger FastAPI

Dans un premier terminal, garder le serveur actif.

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Dans un deuxième terminal PowerShell, interroger les trois endpoints. La première réponse indique `disponible`, la deuxième expose la version `1.0.0` et ses variables, et la troisième contient une probabilité finie, le niveau de risque et la version. Arrêter le serveur avec Ctrl+C après la vérification.

```powershell
$base = 'http://127.0.0.1:8000'
Invoke-RestMethod -Uri "$base/health"
Invoke-RestMethod -Uri "$base/model-info"
$demande = @{
    age = 35
    revenu_mensuel = 250000
    montant_credit = 1000000
    duree_mois = 12
    anciennete_activite = 4
} | ConvertTo-Json
Invoke-RestMethod -Uri "$base/predict" -Method Post -ContentType 'application/json' -Body $demande
```

### Exécuter Ruff, les tests et la couverture

Les tests démarrent leur propre application et construisent des artefacts temporaires. Les commandes exportent les résultats dans un dossier de travail temporaire distinct des preuves archivées.

```powershell
$sortie = Join-Path $env:TEMP ('creditrisk-tp2-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $sortie | Out-Null
Remove-Item Env:CREDITRISK_ECHEC_VOLONTAIRE -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m ruff check .
$pytestArgs = @(
    '--cov=app'
    '--cov-report=term-missing'
    "--cov-report=xml:$sortie/coverage.xml"
    "--junitxml=$sortie/junit.xml"
)
.\.venv\Scripts\python.exe -m pytest @pytestArgs
```

Résultat de référence de la version enrichie : 51 succès, 1 test volontaire ignoré, 95 % de couverture. Pour vérifier précisément la version candidate, exécuter la sélection ci-dessous. Elle donne 25 succès, y compris le contrôle du modèle absent partagé entre les versions.

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py tests/test_integration.py tests/test_robustness.py -k '1.0.1 or test_modele_indisponible'
```

### Reproduire la comparaison et la performance

Le protocole écrit `protocole.json` et `mesures.json` dans le dossier indiqué. Le rappel et le F1 sont reproductibles avec les mêmes dépendances. Les temps et le débit varient selon la machine et la charge.

```powershell
$reproduction = Join-Path $sortie 'mesures'
.\.venv\Scripts\python.exe -m reports.protocole_executable --output-dir $reproduction
Get-ChildItem $reproduction
```

### Reproduire l’échec volontaire en local

L’activation vaut pour le terminal courant pendant ce contrôle. Le résultat attendu est 1 échec volontaire, 51 succès et un code de sortie 1. Le bloc `finally` retire la variable après le test.

```powershell
$env:CREDITRISK_ECHEC_VOLONTAIRE = '1'
try {
    .\.venv\Scripts\python.exe -m pytest -q
    $code = $LASTEXITCODE
    "Code de sortie Pytest : $code"
} finally {
    Remove-Item Env:CREDITRISK_ECHEC_VOLONTAIRE
}
```

