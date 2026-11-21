from concurrent.futures import ThreadPoolExecutor
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
import importlib.metadata as md
import json
import os
import platform
import sys
import joblib
import numpy as np
from fastapi.testclient import TestClient
from sklearn.metrics import recall_score, f1_score, confusion_matrix
from app.main import creer_app
from app.prediction import predire
from app.training import entrainer_reference
from app.validation import DemandeCredit

d = dict(
    age=35,
    revenu_mensuel=250000,
    montant_credit=1000000,
    duree_mois=12,
    anciennete_activite=4,
)
protocole = dict(
    graine_evaluation=2026,
    taille=1000,
    candidat="1.0.1 expérimental : C=0.5",
    seuil=0.5,
    baisse_max_rappel=0.02,
    baisse_max_f1=0.02,
    delta_max_rechargement=1e-12,
    p95_http_ms_max=100,
    debit_requetes_s_min=20,
    concurrence=[1, 4, 8],
    requetes_par_palier=240,
)
parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", type=Path, required=True)
root = parser.parse_args().output_dir
root.mkdir(parents=True, exist_ok=True)
if any((root / name).exists() for name in ("protocole.json", "mesures.json")):
    parser.error("Le dossier contient déjà des résultats. Choisir un nouveau dossier.")
(root / "protocole.json").write_text(
    json.dumps(protocole, ensure_ascii=False, indent=2), encoding="utf-8"
)
ref = entrainer_reference()
candidate = entrainer_reference(regularisation=0.5, version="1.0.1")
rng = np.random.default_rng(protocole["graine_evaluation"])
n = protocole["taille"]
age, rev, amount, duration, seniority = [
    rng.integers(lo, hi, n)
    for lo, hi in [(21, 66), (75000, 750001), (100000, 5000001), (6, 37), (0, 16)]
]
x = np.column_stack((age, rev, amount, duration, seniority))
y = rng.binomial(
    1, 1 / (1 + np.exp(-(-1.5 + 3 * amount / (duration * rev) - 0.05 * seniority)))
)
result = dict(
    environment=dict(
        os=platform.platform(),
        python=sys.version.split()[0],
        cpu=os.environ.get("PROCESSOR_IDENTIFIER"),
        logical_cpus=os.cpu_count(),
        packages={
            k: md.version(k)
            for k in ["fastapi", "scikit-learn", "numpy", "httpx", "uvicorn"]
        },
    ),
    observations={},
    metrics={},
    performance=[],
)


def obs(client, name, body=None, content=None, path="/predict"):
    r = (
        client.get(path)
        if path != "/predict"
        else client.post(
            path, content=content, headers={"content-type": "application/json"}
        )
        if content is not None
        else client.post(path, json=body)
    )
    result["observations"][name] = dict(http=r.status_code, reponse=r.json())


def summary(times, elapsed=None):
    return dict(
        n=len(times),
        median_ms=float(np.median(times)),
        p95_ms=float(np.percentile(times, 95)),
        **({"debit": len(times) / elapsed} if elapsed else {}),
    )


with TemporaryDirectory() as tmp:
    base = Path(tmp) / "reference.joblib"
    joblib.dump(ref, base)
    for art in (ref, candidate):
        model = art["modele"]
        p = model.predict_proba(x)[:, 1]
        assert np.isfinite(p).all() and ((0 <= p) & (p <= 1)).all()
        yp = p >= 0.5
        dest = Path(tmp) / (art["version"] + ".joblib")
        joblib.dump(art, dest)
        pp = joblib.load(dest)["modele"].predict_proba(x)[:, 1]
        with TestClient(creer_app(dest)) as smoke:
            response = smoke.post("/predict", json=d)
            assert response.status_code == 200
            body = response.json()
            assert set(body) == {
                "probabilite_defaut",
                "niveau_risque",
                "version_modele",
            }
            assert body["version_modele"] == art["version"]
        result["metrics"][art["version"]] = dict(
            rappel=recall_score(y, yp),
            f1=f1_score(y, yp),
            matrice=confusion_matrix(y, yp).tolist(),
            delta_rechargement=float(np.abs(p - pp).max()),
            http=body,
        )
    with TestClient(creer_app(base)) as c:
        obs(c, "valide", d)
        obs(c, "health", path="/health")
        obs(c, "model-info", path="/model-info")
        obs(c, "manquant", {k: v for k, v in d.items() if k != "age"})
        for name, k, v in [
            ("age negatif", "age", -1),
            ("revenu texte", "revenu_mensuel", "250000"),
            ("montant nul", "montant_credit", 0),
            ("montant negatif", "montant_credit", -1),
            ("duree fractionnaire", "duree_mois", 12.5),
            ("extra", "extra", True),
            ("montant extreme", "montant_credit", 10**12),
            ("age min", "age", 18),
            ("age max", "age", 100),
            ("hors distribution", "montant_credit", 1_000_000_000),
            ("coherence age anciennete", "anciennete_activite", 82),
        ]:
            obs(c, name, d | {k: v})
        for name, value in [
            ("inf", float("inf")),
            ("-inf", float("-inf")),
            ("NaN", float("nan")),
        ]:
            obs(c, name, content=json.dumps(d | {"revenu_mensuel": value}))
        obs(c, "schema liste", [])
        obs(c, "JSON mal forme", content="{")
        en = DemandeCredit.model_validate(d)
        for i in range(30):
            c.post("/predict", json=d)
            predire(ref["modele"], en)
        times = []
        for i in range(500):
            t = perf_counter()
            predire(ref["modele"], en)
            times.append((perf_counter() - t) * 1000)
        result["inference"] = summary(times)

        def hit(_):
            t = perf_counter()
            r = c.post("/predict", json=d)
            return (perf_counter() - t) * 1000, r.status_code

        for workers in protocole["concurrence"]:
            t = perf_counter()
            with ThreadPoolExecutor(max_workers=workers) as pool:
                rows = list(pool.map(hit, range(protocole["requetes_par_palier"])))
            elapsed = perf_counter() - t
            result["performance"].append(
                dict(
                    concurrence=workers,
                    erreurs=sum(code != 200 for _, code in rows),
                    **summary([ms for ms, _ in rows], elapsed),
                )
            )
    with TestClient(creer_app(Path(tmp) / "absent.joblib")) as c:
        obs(c, "modele absent", d)
        obs(c, "health absent", path="/health")
        obs(c, "model-info absent", path="/model-info")
a, b = result["metrics"].values()
result["non_regression_ok"] = bool(
    b["rappel"] >= a["rappel"] - protocole["baisse_max_rappel"]
    and b["f1"] >= a["f1"] - protocole["baisse_max_f1"]
    and max(a["delta_rechargement"], b["delta_rechargement"])
    <= protocole["delta_max_rechargement"]
)
(root / "mesures.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {k: v for k, v in result.items() if k != "observations"},
        ensure_ascii=False,
        indent=2,
    )
)
if not result["non_regression_ok"]:
    sys.exit("Non-regression: seuil de tolerance depasse. Consulter mesures.json.")
