# Rapport de non-régression

La référence est le pipeline 1.0.0 livré. Le candidat expérimental 1.0.1 conserve les 600 demandes d’entraînement et change uniquement la régularisation de la régression logistique (`C=0.5`). La comparaison repose sur 1 000 nouvelles observations synthétiques générées avec la graine 2026, selon le même mécanisme de simulation. L’artefact candidat est produit pour le contrôle et utilisé temporairement.

Avant les mesures, le [protocole](protocole.json) fixe un seuil de classification de 0,5, une baisse maximale de 2 points de pourcentage pour le rappel et le F1-score et un écart de 10⁻¹² après rechargement du même modèle.

| Critère | Référence | Candidat | Écart | Bilan |
| --- | --- | --- | --- | --- |
| Rappel du défaut | 54,52 % | 54,52 % | 0,00 pt | Conforme |
| F1-score | 61,99 % | 62,09 % | +0,10 pt | Conforme |
| Faux négatifs / défauts simulés | 166 / 365 | 166 / 365 | 0 | Risque résiduel |
| Écart maximal après rechargement | 0 | 0 | 0 | Conforme |
| Contrat HTTP sur la demande témoin | 200, score fini, version 1.0.0 | 200, score fini, version 1.0.1 | Version attendue | Conforme |

Les tests d’API, d’intégration et de robustesse passent sur chacun des deux modèles. Pour le candidat, la sélection ciblée donne **25 succès** : 24 cas utilisant le modèle 1.0.1 et 1 vérification commune du modèle absent. Les mêmes assertions portent sur les codes HTTP, le schéma de sortie, la cohérence du niveau de risque, les métadonnées et les erreurs. Le calcul sur le corpus confirme également que les 1 000 probabilités sont finies et dans l’intervalle attendu. [Preuve JUnit des deux versions](preuves/junit.xml). Les deux versions manquent 45,48 % des défauts simulés. Les tolérances comparent les versions entre elles. L’acceptation métier demande ses propres seuils et des données représentatives.

![Rappel, F1-score et matrice de confusion de la référence](figures/non-regression.png)
