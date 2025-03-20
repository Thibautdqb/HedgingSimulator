# Portefeuille de Gestion Active avec Couverture Dynamique

Bienvenue dans l'application de gestion active de portefeuille avec couverture dynamique ! Cette application permet aux utilisateurs de gérer leurs portefeuilles d'actifs financiers en temps réel, avec des stratégies de couverture sophistiquées pour minimiser les risques.

## Table des matières

- [Présentation de l'application](#présentation-de-lapplication)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Jeux de données](#jeux-de-données)
- [Flux de travail de l'application](#flux-de-travail-de-lapplication)
- [Licence et Gestion des Utilisateurs](#licence-et-gestion-des-utilisateurs)
- [Technologies utilisées](#technologies-utilisées)

---

## Présentation de l'application

Cette application permet de gérer activement un portefeuille d'actifs financiers, en utilisant des stratégies de couverture telles que le **delta-hedging**, **gamma-hedging**, **vega-hedging** et **theta-hedging**. Elle offre une interface utilisateur pour ajouter, ajuster et surveiller les positions, tout en optimisant la couverture pour minimiser le risque global.

L'application intègre également une gestion d'utilisateur, une licence payante et un suivi des flux de données en temps réel via une architecture distribuée, garantissant des performances et des résultats de couverture en temps réel.

---

## Fonctionnalités principales

### **Gestion Active du Portefeuille :**
- **Suivi en temps réel** des rendements et des risques associés aux actions du portefeuille.
- **Ajout et retrait dynamique** d'actifs financiers.
- **Optimisation de la couverture** en fonction des stratégies choisies.
- **Visualisation interactive** des performances du portefeuille et des stratégies de couverture.

### **Stratégies de Couverture Dynamiques :**
- Calculs et ajustement des **grecs** (delta, gamma, vega, theta).
- Couverture en fonction des **matrices de covariance** et de **corrélation**.
- **Optimisation de la couverture** avec **CVXPY** (dynamique, en fonction du risque et de la liquidité).
- **Réduction des risques** à travers une couverture en temps réel.

### **Visualisation Interactive :**
- **Graphiques interactifs** avec **Plotly** pour visualiser la couverture, les risques, et les rendements.
- **Heatmaps** des matrices de covariance et de corrélation.
- **Diagrammes de performance** (volatilité vs. rendement, frontière efficiente).

### **Exportation des Données :**
- **Exportation des données** de portefeuille et des résultats d'optimisation sous format Excel pour un suivi détaillé.
- Sauvegarde des logs des requêtes dans un fichier **JSON** pour la traçabilité.

### **Gestion des Utilisateurs et Licence :**
- Création d'un **identifiant unique** pour chaque utilisateur via **Redis**.
- **Licence payante à 20€** pour débloquer des fonctionnalités avancées.
- Suivi des informations de couverture et de portefeuille via Redis pour chaque utilisateur.

---

## Jeux de données

L'application utilise plusieurs jeux de données pour permettre la gestion et l'optimisation du portefeuille :

- **Données d'Actifs (all_data)** : 
  - Contient les prix de clôture des actifs, les rendements log et les matrices de covariance et de corrélation. Ces données alimentent les calculs de risques du portefeuille.

- **Données du Portefeuille (portfolio_df)** :
  - Contient les positions actuelles de l'utilisateur (identifiants des actions, quantités, dates d'achat, etc.). Ces données sont utilisées pour calculer l'exposition actuelle du portefeuille.

- **Informations sur la Couverture (hedging_info)** :
  - Contient la stratégie de couverture choisie, la couverture cible, et la partie du portefeuille à couvrir. Ces informations orientent l'optimisation du portefeuille.

- **Données des Options (options_df)** :
  - Contient les informations sur les options disponibles pour la couverture (prix, grecs, volatilité implicite, etc.). Ces données sont utilisées dans l'optimisation des positions.

- **Portefeuille Enrichi (enriched_portfolio_df)** :
  - Contient des données enrichies sur les positions du portefeuille (prix actuels, valeurs des positions, pondérations, etc.). Utilisé pour calculer l'exposition dynamique en fonction des positions réelles.

---

## Flux de travail de l'application

### 1. **Chargement des Données**
- Les données du portefeuille et des options sont récupérées et stockées dans **Redis** pour chaque utilisateur.
- Les informations historiques sont téléchargées depuis **yFinance** pour alimenter les rendements et les matrices de covariance.

### 2. **Calcul de l'Exposition du Portefeuille**
- L'exposition est calculée soit pour l'ensemble du portefeuille, soit pour une partie spécifique selon les préférences de l'utilisateur.
- Les expositions sont ajustées en fonction de la stratégie de couverture choisie.

### 3. **Optimisation de la Couverture**
- L'application utilise des méthodes d'optimisation pour ajuster les positions dans le portefeuille et minimiser le risque global.
- Les contraintes sont définies en fonction de la liquidité, des risques de marché, et des objectifs de couverture de l'utilisateur.

### 4. **Visualisation et Suivi**
- Les résultats sont affichés sous forme de graphiques interactifs (**performance**, **couverture**, **risques**).
- Les utilisateurs peuvent ajuster la stratégie de couverture et voir les effets en temps réel.

### 5. **Exportation et Sauvegarde**
- Les résultats d'optimisation et les données du portefeuille peuvent être exportés au format **Excel**.
- Les logs des requêtes sont enregistrés dans un fichier **JSON** pour la traçabilité et la gestion des sessions.

---

## Licence et Gestion des Utilisateurs

### Licence à 20€
Cette application propose une licence payante à **20€** pour débloquer des fonctionnalités avancées telles que :
- Accès aux stratégies de couverture avancées (gamma, vega, theta).
- Optimisation des portefeuilles avec des modèles plus complexes.
- Accès à des graphiques interactifs et à des visualisations de performance.

### Gestion des utilisateurs
La gestion des utilisateurs est effectuée via un identifiant unique généré pour chaque utilisateur à l'aide de **Redis**. Les utilisateurs peuvent s'inscrire et accéder à leurs portefeuilles en toute sécurité. Les données sont stockées de manière isolée pour chaque utilisateur, garantissant ainsi la confidentialité et la sécurité des informations.

---

## Technologies utilisées

- **Flask** : Framework web pour le backend.
- **Redis** : Base de données en mémoire pour la gestion des sessions et des données utilisateur.
- **yFinance** : API pour récupérer les données financières en temps réel.
- **cvxpy** : Bibliothèque pour la résolution des problèmes d'optimisation (couverture).
- **Plotly** : Bibliothèque pour la visualisation interactive des résultats.
- **Celery** : Gestion des tâches asynchrones (optimisation en arrière-plan).
- **Pandas et NumPy** : Manipulation des données financières et calculs mathématiques.

---

### Stratégie de Couverture du Portefeuille

1. **Chargement des Données**
   - **Données d'Actifs (all_data)** : Contient les prix de clôture des actifs, les rendements log, et les matrices de covariance et de corrélation. Ces données alimentent les calculs de risques du portefeuille.
   - **Données des Options (options_df)** : Contient les informations sur les options disponibles pour la couverture (prix, grecs, volatilité implicite, etc.).
   - **Informations de Couverture (hedging_info)** : Contient la stratégie de couverture choisie, la couverture cible, et la partie du portefeuille à couvrir.
   - **Données sur le Portefeuille Actuel (enriched_portfolio_data)** : Contient les informations sur les positions actuelles en actions du portefeuille.

2. **Calcul de l'Exposition du Portefeuille**
   - **Exposition totale si coveringpart == "All"** : Calculé comme la somme des valeurs des positions en actions du portefeuille.
   - **Exposition partielle selon coveringpart spécifié** : Calculé en fonction des positions spécifiques (StockID).
   - **Détails du calcul de l'exposition pour chaque action** :
     - **Exposition pour chaque action** : Calcul de l'exposition d'une action en fonction de la quantité détenue et de la valeur actuelle de l'action.
     - **PositionValue** : Utilisation de la colonne `PositionValue` dans `enriched_portfolio_data` pour obtenir l'exposition en valeur de chaque position.
     - **Couverture en fonction du type de couverture** : L'exposition de chaque action peut être ajustée selon la couverture choisie (delta, gamma, etc.).

3. **Calcul des Matrices de Covariance et de Corrélation**
   - **Matrice de Covariance (liens entre actifs)** : Utilisée pour estimer les risques et la volatilité du portefeuille.
   - **Matrice de Corrélation (force des relations entre actifs)** : Utilisée pour évaluer la diversification entre les actifs.
   - **Nouvelle utilisation des matrices pour optimiser la couverture** :
     - Utilisation de la Matrice de Covariance pour Calculer le Risque Global.
     - Utilisation de la Matrice de Corrélation pour Ajuster les Poids des Options.

4. **Optimisation de la Couverture**
   - **Objectif : Minimiser l'Écart à Zéro (grecs)** :
     - Delta-Hedging : Minimiser Delta.
     - Gamma-Hedging : Minimiser Gamma.
     - Vega-Hedging : Minimiser Vega.
     - Theta-Hedging : Minimiser Theta.
   - **Contraintes** :
     - Couverture Cible (exposition cible).
     - Liquidité (contraintes sur l'intérêt ouvert).
     - Diversification (Call et Put).
     - Neutralisation des Grecs.

5. **Calcul Dynamique de l'Exposition**
   - **Calcul initial de l'exposition du portefeuille** :
     - Si `coveringpart == "All"` : Exposition totale du portefeuille.
     - Si `coveringpart spécifié` : Exposition partielle selon les actifs ciblés.
   - **Ajustement dynamique de l'exposition selon le type de couverture choisi** :
     - Delta-Hedging : Neutralisation de la sensibilité au prix de l'actif sous-jacent.
     - Gamma-Hedging : Neutralisation de la variation du delta.
     - Vega-Hedging : Neutralisation de la sensibilité à la volatilité.
     - Theta-Hedging : Neutralisation de la perte de valeur au fil du temps.

6. **Résultats et Évaluation**
   - Quantité optimale d'options.
   - Coût total de la couverture.
   - Volatilité du portefeuille et corrélation des actifs.
   - Risque global du portefeuille (calculé avec la covariance).
   - Ajustement des options en fonction des corrélations et des risques globaux.

7. **Retour au Frontend (affichage des résultats)**
   - Stratégie optimale et options sélectionnées.
   - Coût de la couverture et exposition cible.
   - Volatilité et risques résiduels.
   - Résultats visuels sur la couverture (graphiques et tableaux).

---

Ce **README** présente toutes les informations détaillées concernant l'application de gestion de portefeuille avec couverture dynamique, sa mise en œuvre et ses fonctionnalités essentielles. Vous pouvez l'utiliser comme un guide pour utiliser l'application ou comme référence pour le développement.
