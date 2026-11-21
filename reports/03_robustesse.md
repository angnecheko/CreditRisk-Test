# Robustesse et registre des anomalies

| Cas | Risque visé | Comportement attendu | Observé | Anomalie |
| --- | --- | --- | --- | --- |
| ROB-01 | Calcul sur NaN ou infini | Rejet des trois valeurs non finies | 422, `finite_number` | Aucune |
| ROB-02 | Rejet incorrect des bornes | Acceptation des âges 18 et 100 | 200 aux deux bornes | Aucune |
| ROB-03 | Schéma incorrect | Rejet d’une liste JSON et des champs supplémentaires | 422, `model_attributes_type` ou `extra_forbidden` | Aucune |
| ROB-04 | Imputation implicite ou conversion d’une chaîne | Rejet d’un champ manquant et d’un revenu texte | 422, `missing` ou `float_type` | Aucune |
| ROB-05 | Score peu fiable hors distribution | Valeur dans le schéma acceptée et signalement souhaité pour examen | 200 pour 1 milliard FCFA, sans alerte | A01 · majeure avant pilote |
| ROB-06 | Profil contradictoire | Rejet ou signalement souhaité pour âge 35 et ancienneté 82 ans | 200, sans contrôle croisé | A02 · majeure avant pilote |

Le tableau JSON vide est rejeté par `test_rejette_un_tableau_json`. Les deux entrées inhabituelles sont désormais contrôlées par `test_entrees_valides_selon_le_schema` pour les deux modèles. Le test fixe le contrat actuel : HTTP 200 et probabilité conforme. Le signalement hors distribution et la cohérence croisée restent des exigences métier à définir avant le pilote. Les [réponses détaillées](mesures.json) et le [journal des assertions](preuves/junit.xml) conservent les résultats.

| Anomalie et cas source | Gravité proposée | Correction recommandée | Statut |
| --- | --- | --- | --- |
| A01 (ROB-05) · Pas de signalement hors distribution | Majeure avant pilote | Définir les plages avec le métier et orienter les dossiers signalés vers une revue humaine | Ouverte |
| A02 (ROB-06) · Ancienneté incompatible avec l’âge | Majeure avant pilote | Définir une règle métier de cohérence croisée puis ajouter des tests | Ouverte |
| A03 (journal Pytest) · Dépréciation Starlette | Mineure | Vérifier la compatibilité des dépendances lors de leur prochaine mise à jour | Ouverte |
