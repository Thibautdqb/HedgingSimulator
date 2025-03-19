# HedgingSimulator


# Stratégie de Couverture du Portefeuille

## 1. Chargement des Données
- **Données d'Actifs** (`all_data`)
- **Données des Options** (`options_df`)
- **Informations de Couverture** (`hedging_info`)
- **Données sur le Portefeuille Actuel** (`enriched_portfolio_data`)
  - Contient les informations sur les positions actuelles en actions

## 2. Calcul de l'Exposition du Portefeuille
- **Exposition totale si coveringpart == "All"**
  - Calculé comme la somme des valeurs des positions en actions du portefeuille
- **Exposition partielle selon coveringpart spécifié**
  - Calculé en fonction des positions spécifiques (`StockID`)

### Détails du calcul de l'exposition pour chaque action :
- **Exposition pour chaque action** :
  - **Valeur des Positions** : Calcul de l'exposition d'une action en fonction de la quantité détenue et de la valeur actuelle de l'action.
    - Exemple : `exposure_action = position_quantity * current_price`
  - **PositionValue** : Utilisation de la colonne `PositionValue` dans `enriched_portfolio_data` pour obtenir l'exposition en valeur de chaque position.
    - Exemple : `exposure_action = enriched_portfolio_df['PositionValue']`
  - **Couverture en fonction du type de couverture** : L'exposition de chaque action peut être ajustée selon la couverture choisie (delta, gamma, etc.).
    - Exemple : Pour delta-hedging, l'exposition à chaque action pourrait être ajustée en fonction du delta associé à cette action.
- **Exposition dynamique selon le type de couverture**
  - L'exposition du portefeuille est ajustée pour chaque action en fonction du type de couverture (delta, gamma, etc.).

## 3. Calcul des Matrices de Covariance et de Corrélation
- **Matrice de Covariance** (liens entre actifs)
  - Utilisée pour estimer les risques et la volatilité du portefeuille
- **Matrice de Corrélation** (force des relations entre actifs)
  - Utilisée pour évaluer la diversification entre les actifs

### Nouvelle utilisation des matrices pour optimiser la couverture
- **Utilisation de la Matrice de Covariance pour Calculer le Risque Global**
  - Contraintes sur le risque total du portefeuille (ex. `quad_form(x, cov_matrix)`)
- **Utilisation de la Matrice de Corrélation pour Ajuster les Poids des Options**
  - Ajustement des poids pour réduire l'impact des actifs fortement corrélés

## 4. Optimisation de la Couverture
- **Objectif : Minimiser l'Écart à Zéro (grecs)**
  - **Delta-Hedging** : Minimiser Delta
  - **Gamma-Hedging** : Minimiser Gamma
  - **Vega-Hedging** : Minimiser Vega
  - **Theta-Hedging** : Minimiser Theta
- **Contraintes :**
  - Couverture Cible (exposition cible)
  - Liquidité (contraintes sur l'intérêt ouvert)
  - Diversification (Call et Put)
  - Neutralisation des Grecs
- **Résolution de l'Optimisation** (CVXPY)

## 5. Calcul Dynamique de l'Exposition
- **Calcul initial de l'exposition du portefeuille**
  - Si `coveringpart == "All"` : Exposition totale du portefeuille
  - Si `coveringpart` spécifié : Exposition partielle selon les actifs ciblés
- **Ajustement dynamique de l'exposition selon le type de couverture choisi :**
  - **Delta-Hedging** : Neutralisation de la sensibilité au prix de l'actif sous-jacent
  - **Gamma-Hedging** : Neutralisation de la variation du delta
  - **Vega-Hedging** : Neutralisation de la sensibilité à la volatilité
  - **Theta-Hedging** : Neutralisation de la perte de valeur au fil du temps
- **Exemple de calcul dynamique :**
  - `portfolio_exposure * target_coverage` (ajusté selon la couverture)

## 6. Résultats et Evaluation
- **Quantité optimale d'options**
- **Coût total de la couverture**
- **Volatilité du portefeuille et corrélation des actifs**
- **Risque global du portefeuille** (calculé avec la covariance)
- **Ajustement des options en fonction des corrélations et des risques globaux**
- **Performance de la couverture** (comparaison avant-après couverture)

## 7. Retour au Frontend (affichage des résultats)
- Stratégie optimale et options sélectionnées
- Coût de la couverture et exposition cible
- Volatilité et risques résiduels
- Résultats visuels sur la couverture (graphiques et tableaux)


# Visualisation des Échanges de Données dans l'Application

## Diagramme Mermaid : Échanges entre Utilisateur, Frontend, Flask Backend, Redis, Celery, yfinance, et Plotly

Voici une visualisation des échanges de données dans votre application, représentée sous forme de diagramme Mermaid :

### Diagramme des échanges (Sequence Diagram)

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Frontend (HTML/JS)
    participant Flask as Flask Backend
    participant Redis
    participant Celery
    participant yfinance
    participant Plotly

    User->>Frontend: 1. Soumet formulaire portfolio (POST /api/portfolio-modeling)
    Frontend->>Flask: 2. Données JSON (positions)
    Flask->>Redis: 3. Stocke portfolio_df_{user_id}
    
    User->>Frontend: 4. Demande historique (GET /get_historical_data)
    Frontend->>Flask: 5. Requête historique
    Flask->>yfinance: 6. Récupère données marché
    yfinance-->>Flask: 7. Données historiques
    Flask->>Redis: 8. Stocke all_data_{user_id}
    
    User->>Frontend: 9. Accède visualisation (GET /Visualization)
    Frontend->>Flask: 10. Requête visualisation
    Flask->>Redis: 11. Récupère all_data + portfolio_df
    Flask->>Plotly: 12. Génère graphiques
    Plotly-->>Flask: 13. HTML des visualisations
    Flask-->>Frontend: 14. Page avec graphiques
    
    User->>Frontend: 15. Configure hedging (POST /api/delta)
    Frontend->>Flask: 16. Paramètres hedging
    Flask->>Redis: 17. Stocke hedging_info_{user_id}
    
    User->>Frontend: 18. Lance calcul hedging (GET /hedge)
    Frontend->>Flask: 19. Requête optimisation
    Flask->>Redis: 20. Récupère toutes données
    Flask->>Celery: 21. Tâche d'optimisation
    Celery->>Flask: 22. Résultats optimisation
    Flask->>Redis: 23. Stocke options_df_{user_id}
    Flask-->>Frontend: 24. Résultats couverture
    
    User->>Frontend: 25. Export Excel (GET /export_to_xlsx)
    Frontend->>Flask: 26. Requête export
    Flask->>Redis: 27. Récupère all_data
    Flask-->>Frontend: 28. Fichier Excel




graph LR
A[Requête] --> B[Log dans analytics.json]
B --> C[Analyse temps réel]
C --> D[Dashboard Plotly]
