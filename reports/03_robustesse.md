# Robustesse et registre des anomalies

| Cas | Risque visé | Comportement attendu | Observé |
| --- | --- | --- | --- |
| ROB-01 | Calcul sur NaN ou infini | Rejet des trois valeurs non finies | 422, `finite_number` |
| ROB-02 | Rejet incorrect des bornes | Acceptation des âges 18 et 100 | 200 aux deux bornes |
| ROB-03 | Schéma incorrect | Rejet d’une liste JSON et des champs supplémentaires | 422, `model_attributes_type` ou `extra_forbidden` |
| ROB-04 | Imputation implicite ou conversion d’une chaîne | Rejet d’un champ manquant et d’un revenu texte | 422, `missing` ou `float_type` |
| ROB-05 | Score peu fiable hors distribution | Valeur dans le schéma acceptée et signalement souhaité pour examen | 200 pour 1 milliard FCFA, sans alerte |
| ROB-06 | Profil contradictoire | Rejet ou signalement souhaité pour âge 35 et ancienneté 82 ans | 200, sans contrôle croisé |

Les cas ROB-03 (liste), ROB-05 et ROB-06 ont été sondés en complément de la suite automatisée. Les réponses sont consignées dans [mesures.json](mesures.json).

| Anomalie | Gravité proposée | Correction recommandée |
| --- | --- | --- |
| A01 · Pas de signalement hors distribution | Majeure avant pilote | Définir les plages avec le métier et orienter les dossiers signalés vers une revue humaine |
| A02 · Ancienneté incompatible avec l’âge | Majeure avant pilote | Définir une règle métier de cohérence croisée puis ajouter des tests |
| A03 · Dépréciation Starlette | Mineure | Vérifier la compatibilité des dépendances lors de leur prochaine mise à jour |
