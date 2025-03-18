# HedgingSimulator





Stratégie de Couverture du Portefeuille
│
├── 1. Chargement des Données
│   ├── Données d'Actifs (all_data)
│   ├── Données des Options (options_df)
│   ├── Informations de Couverture (hedging_info)
│   └── Données sur le Portefeuille Actuel (enriched_portfolio_data)
│       └── Contient les informations sur les positions actuelles en actions
│
├── 2. Calcul de l'Exposition du Portefeuille
│   ├── Exposition totale si coveringpart == "All"
│   │   └── Calculé comme la somme des valeurs des positions en actions du portefeuille
│   └── Exposition partielle selon coveringpart spécifié
│       └── Calculé en fonction des positions spécifiques (StockID)
│
│   # Détails du calcul de l'exposition pour chaque action :
│   ├── **Exposition pour chaque action** :
│   │   ├── **Valeur des Positions** : Calcul de l'exposition d'une action en fonction de la quantité détenue et de la valeur actuelle de l'action.
│   │   │   └── Exemple : `exposure_action = position_quantity * current_price`
│   │   ├── **PositionValue** : Utilisation de la colonne `PositionValue` dans `enriched_portfolio_data` pour obtenir l'exposition en valeur de chaque position.
│   │   │   └── Exemple : `exposure_action = enriched_portfolio_df['PositionValue']`
│   │   ├── **Couverture en fonction du type de couverture** : L'exposition de chaque action peut être ajustée selon la couverture choisie (delta, gamma, etc.).
│   │   │   └── Exemple : Pour delta-hedging, l'exposition à chaque action pourrait être ajustée en fonction du delta associé à cette action.
│   └── Exposition dynamique selon le type de couverture
│       └── L'exposition du portefeuille est ajustée pour chaque action en fonction du type de couverture (delta, gamma, etc.).
│
├── 3. Calcul des Matrices de Covariance et de Corrélation
│   ├── Matrice de Covariance (liens entre actifs)
│   │   └── Utilisée pour estimer les risques et la volatilité du portefeuille
│   ├── Matrice de Corrélation (force des relations entre actifs)
│   │   └── Utilisée pour évaluer la diversification entre les actifs
│
│   # Nouvelle utilisation des matrices pour optimiser la couverture
│   ├── Utilisation de la Matrice de Covariance pour Calculer le Risque Global
│   │   └── Contraintes sur le risque total du portefeuille (ex. quad_form(x, cov_matrix))
│   ├── Utilisation de la Matrice de Corrélation pour Ajuster les Poids des Options
│   │   └── Ajustement des poids pour réduire l'impact des actifs fortement corrélés
│
├── 4. Optimisation de la Couverture
│   ├── Objectif : Minimiser l'Écart à Zéro (grecs)
│   │   ├── Delta-Hedging : Minimiser Delta
│   │   ├── Gamma-Hedging : Minimiser Gamma
│   │   ├── Vega-Hedging : Minimiser Vega
│   │   └── Theta-Hedging : Minimiser Theta
│   ├── Contraintes :
│   │   ├── Couverture Cible (exposition cible)
│   │   ├── Liquidité (contraintes sur l'intérêt ouvert)
│   │   ├── Diversification (Call et Put)
│   │   └── Neutralisation des Grecs
│   └── Résolution de l'Optimisation (CVXPY)
│
├── 5. Calcul Dynamique de l'Exposition
│   ├── Calcul initial de l'exposition du portefeuille
│   │   ├── Si coveringpart == "All" : Exposition totale du portefeuille
│   │   └── Si coveringpart spécifié : Exposition partielle selon les actifs ciblés
│   ├── Ajustement dynamique de l'exposition selon le type de couverture choisi :
│   │   ├── Delta-Hedging : Neutralisation de la sensibilité au prix de l'actif sous-jacent
│   │   ├── Gamma-Hedging : Neutralisation de la variation du delta
│   │   ├── Vega-Hedging : Neutralisation de la sensibilité à la volatilité
│   │   └── Theta-Hedging : Neutralisation de la perte de valeur au fil du temps
│   └── Exemple de calcul dynamique : 
│       └── portfolio_exposure * target_coverage (ajusté selon la couverture)
│
├── 6. Résultats et Evaluation
│   ├── Quantité optimale d'options
│   ├── Coût total de la couverture
│   ├── Volatilité du portefeuille et corrélation des actifs
│   ├── Risque global du portefeuille (calculé avec la covariance)
│   ├── Ajustement des options en fonction des corrélations et des risques globaux
│   └── Performance de la couverture (comparaison avant-après couverture)
│
└── 7. Retour au Frontend (affichage des résultats)
    ├── Stratégie optimale et options sélectionnées
    ├── Coût de la couverture et exposition cible
    ├── Volatilité et risques résiduels
    └── Résultats visuels sur la couverture (graphiques et tableaux)