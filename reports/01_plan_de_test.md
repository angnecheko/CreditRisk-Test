# Plan de test et matrice de traçabilité

Le périmètre couvre la validation stricte, le prétraitement, la régression logistique et l’API FastAPI. Les 600 demandes d’entraînement sont synthétiques. Les règles métier pour une utilisation réelle restent à établir.

Pour chaque cas, D désigne la demande de référence du README. Les tests HTTP supposent une API initialisée avec le modèle 1.0.0, sauf EX05. P1 indique un risque susceptible de bloquer ou d’altérer une décision. P2 indique un risque de dégradation de service ou de traçabilité. Les tests unitaires et fonctionnels précèdent l’intégration, la robustesse, la comparaison ML et la mesure de performance.

| ID | Exigence et entrée | Cas et résultat attendu | Risque / priorité |
| --- | --- | --- | --- |
| EX01 | Âge entier de 18 à 100, D modifiée | API-03 âge −1 → 422. ROB-02 âges 18 et 100 → 200 | Entrée incohérente / P1 |
| EX02 | Revenu numérique, positif et fini | API-04 chaîne → 422. ROB-01 valeurs non finies → 422 | Calcul invalide / P1 |
| EX03 | Durée entière de 1 à 120 mois | API-06 durée 12,5 → 422 | Unité ou durée incohérente / P1 |
| EX04 | Probabilité finie comprise entre 0 et 1 | API-01 avec D → 200 et score dans l’intervalle | Score inexploitable / P1 |
| EX05 | Artefact absent au démarrage | API-09 avec chemin inexistant → 503 sur les trois endpoints | Service indisponible / P1 |
| EX06 | Tous les champs requis sont présents | API-02 D sans âge → 422 | Prédiction sur données incomplètes / P1 |
| EX07 | Les critères critiques se maintiennent | NR-01 référence et candidat sur 1 000 observations → baisses dans les tolérances | Régression du risque / P1 |
| EX08 | Montant strictement positif et plafonné | API-05 montant nul ou négatif et API-08 montant supérieur au plafond → 422 | Demande financière incohérente / P1 |
| EX09 | Schéma strict et JSON valide | API-07 clé inconnue, API-10 JSON tronqué, ROB-03 liste JSON → 422 | Entrée ambiguë / P1 |
| EX10 | Ordre des variables et version cohérents | INT-01 D → score égal au calcul direct et version égale aux métadonnées | Erreur silencieuse de pipeline / P1 |
| EX11 | Erreurs internes contrôlées | INT-02 à INT-04 injection d’erreur et dimensions invalides → 500 générique | Fuite de détails / P1 |
| EX12 | Prédiction stable après rechargement | NR-02 sauvegarde puis chargement → écart absolu ≤ 10⁻¹² | Déploiement non reproductible / P1 |
| EX13 | Objectif de performance locale | PERF-01 charge 1, 4 et 8 → P95 ≤ 100 ms, ≥ 20 req/s, aucune erreur | Temps de réponse excessif / P2 |

Les résultats attendus sont confrontés aux parcours détaillés dans les rapports suivants.
