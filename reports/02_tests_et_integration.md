# Tests unitaires, fonctionnels et d’intégration

## Résultats des scénarios API

Précondition commune : modèle 1.0.0 chargé et demande du README. API-09 utilise une application démarrée avec un chemin d’artefact absent. Pour les erreurs 422, l’API fournit l’emplacement et le type d’erreur dans `detail`.

| Cas | Entrée | HTTP attendu / observé | Corps et comportement attendus | Résultat observé |
| --- | --- | --- | --- | --- |
| API-01 | D complète | 200 / 200 | Score fini dans [0,1], niveau selon le seuil de 0,5 et version de l’artefact | 0,454323 / risque faible / 1.0.0. Avec le candidat, 0,453576 / risque faible / 1.0.1 |
| API-02 | Âge omis | 422 / 422 | Erreur `missing` localisée sur l’âge, rejet avant prédiction | Conforme |
| API-03 | Âge −1 | 422 / 422 | Erreur `greater_than_equal` sur l’âge, rejet | Conforme |
| API-04 | Revenu « 250000 » | 422 / 422 | Erreur `float_type` sur le revenu, rejet sans conversion | Conforme |
| API-05 | Montant 0 puis −1 | 422 / 422 | Erreur `greater_than` sur le montant, rejet | Même erreur pour les deux valeurs |
| API-06 | Durée 12,5 | 422 / 422 | Erreur `int_type` sur la durée, rejet sans arrondi | Conforme |
| API-07 | Clé supplémentaire | 422 / 422 | Erreur `extra_forbidden` sur la clé, rejet | Conforme |
| API-08 | Montant 10¹² FCFA | 422 / 422 | Erreur `less_than_equal` sur le montant, rejet | Conforme |
| API-09 | D et artefact absent | 503 / 503 | `detail` vaut « Modèle indisponible » sur les trois routes | Conforme sur les trois routes |
| API-10 | Corps JSON tronqué | 422 / 422 | Erreur `json_invalid`, rejet du corps | Conforme |

Les scénarios avec un client initialisé sont rejoués sur la référence et le candidat. Le contrôle d’artefact absent est commun aux deux versions. Les [réponses détaillées de la référence](mesures.json) et le [journal JUnit des deux versions](preuves/junit.xml) permettent de vérifier les résultats.

## Intégration et test unitaire

| Cas | Vérification | Résultat observé |
| --- | --- | --- |
| INT-01 | Disponibilité, ordre des variables, calcul direct et version | 200, score cohérent, métadonnées alignées |
| INT-02 | Exception de prétraitement | 500, « Erreur de prédiction » |
| INT-03 | Dimensions incompatibles | 500, même message générique |
| INT-04 | Exception lors de la prédiction | 500, même message générique |
| INT-05 | Variable indisponible après validation, simulée par un `KeyError` de transformation | 500, message générique sans nom de variable |
| INT-06 | Artefact chargé avec une liste de variables incompatible | 503, « Modèle indisponible » |
| API-02 et API-09 | Champ manquant à la frontière HTTP et artefact absent | 422 avant prédiction et 503 sur les trois routes |
| UNIT-01 | Conservation des montants et revenus en FCFA | Test réussi |

La demande sans âge vérifie aussi que la validation intercepte l’entrée avant l’inférence. La suite locale obtient 51 succès, 1 cas volontaire ignoré et 95 % de couverture des instructions. Un avertissement de dépréciation provient de Starlette.

![Sortie réelle de Pytest, rendue en image](figures/pytest.png)
