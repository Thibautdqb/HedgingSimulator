from flask import Flask, request, jsonify, render_template, redirect, send_file, session, g
import pandas as pd
import yfinance as yf
from datetime import datetime
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import tempfile
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
import plotly.graph_objs as go
import plotly
import numpy as np
import scipy.stats as si
import pandas as pd
##### Approximation du beta pour les options americaine
# Fonction pour calculer le delta d'une option via la formule de Black-Scholes
import io
import base64
import json
import time


import yfinance as yf
from flask_cors import CORS
CORS(app)  # Active CORS pour toutes les routes

app = Flask(__name__)
app.secret_key = 'TFGYUOIZV'

# Créer un DataFrame vide pour stocker les données
portfolio_df = pd.DataFrame(columns=['StockID', 'PositionType', 'StockQty', 'OpenDate'])


###### ANALYTICS
LOG_FILE = os.path.join(os.getcwd(), "analytics.json")  # Assure un chemin absolu


# Vérifier si le fichier existe et est accessible en écriture
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        
        file.write("[]")  # Initialise un JSON vide


        
# Démarrer le chronomètre avant chaque requête
@app.before_request
def start_timer():
    g.start_time = time.time()

# Enregistrer chaque requête dans un fichier JSON
@app.after_request
def log_request(response):
    if request.endpoint not in ['static']:  # Ignore les fichiers statiques
        duration = round(time.time() - g.start_time, 4)
        log_entry = {
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "ip": request.remote_addr,
            "session_id": session.get('session_id', 'unknown'),
            "endpoint": request.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration": duration,
            "user_agent": request.headers.get('User-Agent')
        }

        # Sauvegarde dans un fichier JSON
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as file:
                json.dump([], file)  # Initialise le fichier JSON vide

        with open(LOG_FILE, "r+") as file:
            logs = json.load(file)
            logs.append(log_entry)
            file.seek(0)
            json.dump(logs, file, indent=4)

    return response




@app.route('/analytics')
def show_analytics():
    if not os.path.exists(LOG_FILE):
        return "<h2>Aucun log disponible.</h2>"

    with open(LOG_FILE, "r") as file:
        logs = json.load(file)

    return json.dumps(logs, indent=4)




import pandas as pd
import plotly.express as px
from flask import render_template

@app.route('/analytics-dashboard')
def analytics_dashboard():
    if not os.path.exists(LOG_FILE):
        return "<h2>Aucun log disponible.</h2>"

    with open(LOG_FILE, "r") as file:
        logs = json.load(file)

    if not logs:
        return "<h2>Aucune donnée disponible.</h2>"

    df = pd.DataFrame(logs)

    # 📊 Graphique 1 : Temps de réponse par endpoint
    fig1 = px.line(df, x='timestamp', y='duration', color='endpoint', title="Temps de réponse des endpoints")
    graph1_html = fig1.to_html(full_html=False)

    # 📊 Graphique 2 : Fréquence des endpoints
    endpoint_counts = df['endpoint'].value_counts().reset_index()
    endpoint_counts.columns = ['endpoint', 'count']
    fig2 = px.bar(endpoint_counts, x='endpoint', y='count', title="Fréquence des endpoints")
    graph2_html = fig2.to_html(full_html=False)

    return render_template("analytics.html", graph1=graph1_html, graph2=graph2_html)










@app.route('/session-data', methods=['GET'])
def session_data():
    # Convertir la session en dictionnaire pour l'afficher en JSON
    return jsonify(dict(session))




@app.route('/api/portfolio-modeling', methods=['POST'])
def portfolio_modeling():
    global portfolio_df

    try:
        # Recevoir les données JSON envoyées depuis le frontend
        data = request.get_json()

        # Vérifier que les données sont valides
        if not isinstance(data, list) or not data:
            return jsonify({"error": "Données invalides ou vides."}), 400

        # Convertir les données reçues en un DataFrame et ajouter à celui existant
        new_data = pd.DataFrame(data)

        # Valider que les colonnes sont correctes
        expected_columns = ['stockId', 'positionType', 'stockQty', 'openDate']
        if not all(col in new_data.columns for col in expected_columns):
            return jsonify({"error": "Colonnes incorrectes dans les données."}), 400

        # Renommer les colonnes pour correspondre à celles du DataFrame principal
        new_data.rename(columns={
            'stockId': 'StockID',
            'positionType': 'PositionType',
            'stockQty': 'StockQty',
            'openDate': 'OpenDate'
        }, inplace=True)

        # Ajouter les nouvelles données au DataFrame global
        portfolio_df = pd.concat([portfolio_df, new_data], ignore_index=True)
        portfolio_df.index.name = 'StockIndex'
        portfolio_df['StockID'] = portfolio_df['StockID'].astype(str)
        

        print(portfolio_df)




        # Retourner une réponse de succès
        return jsonify({"message": "Données du portefeuille ajoutées avec succès!"}), 200 

    except Exception as e:
        # Gestion des erreurs
        return jsonify({"error": f"Erreur lors de l'ajout des données : {str(e)}"}), 500



@app.route('/clearsession')
def clear_session():
    session.clear()
    return "Session cleared"


# Route d'accueil pour vérifier que le serveur fonctionne
@app.route('/')
def index():
    return render_template('Index.html')  # Créez un fichier 'templates/index.html'

@app.route('/modelisation')
def modelisation():
    # Ici vous pouvez ajouter des données supplémentaires à la page Modelisation.html si nécessaire
    return render_template('Modelisation.html')  # Redirection vers Modelisation.html


def get_enrich_portfolio_data():
    try:
        # Charger portfolio_df (à remplacer par votre source de données réelle)
        portfolio_infos_file = session.get('portfolio_df')
        if portfolio_infos_file is None:
            print("Aucun fichier portfolio_infos trouvé dans la session.")
            return jsonify({"error": "Aucun fichier portfolio_infos trouvé dans la session."}), 400

        if not os.path.exists(portfolio_infos_file):
            return jsonify({"error": f"Le fichier spécifié n'existe pas: {portfolio_infos_file}"}), 400

        portfolio_df = pd.read_csv(portfolio_infos_file)
        # Partie 1: Enrichissement des données du portefeuille
        def enrich_portfolio_data(df):
            enriched_data = []
            for index, row in df.iterrows():
                ticker = row['StockID']
                try:
                    stock = yf.Ticker(ticker)
                    history = stock.history(period="1d")
                    current_price = history['Close'].iloc[-1]
                    
                    enriched_data.append({
                        'StockID': ticker,
                        'StockQty': row['StockQty'],
                        'OpenDate': row['OpenDate'],
                        'PositionType': row['PositionType'],
                        'CurrentPrice': current_price,
                        'PositionValue': current_price * row['StockQty'],
                    })
                except Exception as e:
                    print(f"Erreur pour {ticker}: {e}")
            return pd.DataFrame(enriched_data)

        enriched_portfolio_df = enrich_portfolio_data(portfolio_df)
        total_portfolio_value = enriched_portfolio_df['PositionValue'].sum()
        enriched_portfolio_df['Weight'] = enriched_portfolio_df['PositionValue'] / total_portfolio_value
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')
        # Sauvegarder le DataFrame dans ce fichier
        enriched_portfolio_df.to_csv(temp_file.name, index=False)

        # Stocker le chemin du fichier dans la session
        session['enriched_portfolio_df'] = temp_file.name

        return jsonify({
            'enriched_portfolio': enriched_portfolio_df.to_dict(orient='records'),
            'portfolio_value': total_portfolio_value,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500



@app.route('/some_route')
def some_route():
    print(dict(session))
    return "Vérifie ta console pour voir le contenu de la session."

@app.route('/check_session_portfolio', methods=['GET'])
def check_session_portfolio():
    portfolio = session.get('enriched_portfolio_df')
    if portfolio:
        return jsonify({
            'enriched_portfolio': portfolio,
            'status': 'success'
        })
    else:
        return jsonify({
            'error': 'Le portefeuille n\'est pas présent dans la session.',
            'status': 'error'
        }), 404



@app.route('/get_historical_data', methods=['GET'])
def get_historical_data():
    try:
        # Partie 2: Téléchargement des données historiques
        portfolio_df['OpenDate'] = pd.to_datetime(portfolio_df['OpenDate'])

        # Identifier la position la plus ancienne
        oldest_position_date = portfolio_df['OpenDate'].min()
        days_since_oldest_position = (datetime.now() - oldest_position_date).days
        print(f"Jours depuis la position la plus ancienne : {days_since_oldest_position}")
        # Calcul de la période de téléchargement (6 fois la période la plus longue)
        max_period_days = 5 * days_since_oldest_position


        print(max_period_days)
        max_period_date = datetime.now() - timedelta(days=max_period_days)
        print(max_period_date)
        # Initialisation des données historiques
        historical_prices = {}

        # Télécharger les données historiques pour chaque StockID
        for index, row in portfolio_df.iterrows():
            ticker = row['StockID']
            open_date = row['OpenDate']

            # Déterminer la plage et l'intervalle en fonction de la durée depuis l'ouverture
            days_since_open = (datetime.now() - open_date).days
            if days_since_open <= 146:
                start_date = (max_period_date).strftime('%Y-%m-%d')
                interval = '1h'  # Agrégation par heure
            else:
                start_date = (max_period_date).strftime('%Y-%m-%d')
                interval = '1d'  # Agrégation quotidienne


            # Appliquer un filtre supplémentaire basé sur 6 fois la période la plus longue
            start_date_filtered = (datetime.now() - timedelta(days=max_period_days)).strftime('%Y-%m-%d')
            start_date = max(start_date, start_date_filtered)  # Prendre la période la plus restrictive

            print(f"Téléchargement des données pour {ticker} depuis {start_date} avec intervalle '{interval}'...")

            try:
                # Télécharger les prix historiques
                stock_data = yf.download(
                    ticker,
                    start=start_date,
                    end=datetime.now().strftime('%Y-%m-%d'),
                    interval=interval
                )

                # Vérifier si des données ont été téléchargées
                if stock_data.empty:
                    print(f"Aucune donnée disponible pour {ticker}.")
                    continue

                # Ajouter les données au dictionnaire
                historical_prices[ticker] = stock_data['Close']

            except Exception as e:
                print(f"Erreur pour le ticker {ticker}: {e}")

        # Vérifier que des données ont été téléchargées
        if not historical_prices:
            raise ValueError("Aucune donnée n'a été téléchargée. Vérifiez vos tickers ou dates.")

        # Afficher un aperçu des données téléchargées
        print("\nDonnées historiques consolidées :")
        for ticker, data in historical_prices.items():
            print(f"{ticker} :")
            print(data.head())

        print("\nContenu du dictionnaire 'historical_prices':")
        for ticker, series in historical_prices.items():
            print(f"{ticker}:")
            print(series.head(), "\n")

        print("\nContenu du dictionnaire 'historical_prices':")

        # Parcourir chaque élément du dictionnaire
        for ticker, series in historical_prices.items():
            # Réinitialiser l'index pour transformer 'Date' en une colonne explicite
            flattened_series = series.reset_index()

            # Ajouter une colonne pour le ticker correspondant
            flattened_series['StockID'] = ticker

            # Renommer les colonnes pour une structure claire
            flattened_series = flattened_series.rename(columns={'Date': f'OpenDate_{ticker}'})
            # Ajouter "Price_" au début de la colonne 3
            if len(flattened_series.columns) > 2:  # Vérifier qu'il existe au moins 3 colonnes
                col_name = flattened_series.columns[1]  # Nom de la colonne à l'index 2
                flattened_series = flattened_series.rename(columns={col_name: f'Price_{ticker}'})

            # Afficher les premières lignes de la série aplatie
            print(f"{ticker} (aplaties) :")

            flattened_series = flattened_series.drop(columns=['StockID'])

            # Remplacer dans le dictionnaire la version aplatie
            historical_prices[ticker] = flattened_series
            print(flattened_series.head(), "\n")
            # Combiner les données historiques en un DataFrame
        all_data = pd.concat(historical_prices, axis=1)

        # Supprimer le niveau 0 du MultiIndex des colonnes
        all_data.columns = all_data.columns.droplevel(0)

        # Supprimer la colonne 'index' si elle existe
        if 'index' in all_data.columns:
            all_data = all_data.drop(columns=['index'], errors='ignore')

# Identifier les colonnes contenant 'Datetime'
        datetime_columns = [col for col in all_data.columns if 'Datetime' in col]
        datetime_columns_to_drop = datetime_columns[1:]  # du 2ème élément à la fin

        # Identifier les colonnes contenant 'Price_OpenDate_*'
        price_opendate_columns = [col for col in all_data.columns if 'OpenDate_' in col]
        date = [col for col in all_data.columns if 'Date' in col]

        # Vérifier s'il existe des colonnes `Datetime`
        if datetime_columns:
            # Conserver uniquement la première colonne datetime et la renommer en 'Date'
            print("Conserver la première colonne `Datetime` et supprimer les autres.")
            all_data = all_data.rename(columns={all_data.columns[0]: 'Date'})
            # Supprimer les colonnes de la forme `Price_OpenDate_*`
            all_data = all_data.drop(columns=datetime_columns_to_drop, errors='ignore')
        else:
            # Aucune colonne datetime n'est détectée
            print("Aucune colonne `Datetime` détectée.")
            # Renommer la première colonne en 'Date'
            all_data = all_data.rename(columns={all_data.columns[0]: 'Date'})
            # Supprimer les colonnes de la forme `Price_OpenDate_*`
            all_data = all_data.drop(columns=price_opendate_columns, errors='ignore')


        if list(all_data.columns).count('Date') > 1:
            all_data = all_data.loc[:, ~all_data.columns.duplicated()].copy()


        # Afficher les colonnes finales pour validation
        print("\nColonnes finales du DataFrame :")
        print(all_data.columns)
        for column in all_data.columns:
            if column.startswith('Price_') and not column.startswith('Price_OpenDate_'):
                ticker = column.replace('Price_', '')  # Extraire le nom du ticker (AAPL, MSFT, etc.)

                # Calculer les rendements logarithmiques
                all_data[f'LogReturn_{ticker}'] = np.log(all_data[column] / all_data[column].shift(1))
        all_data = all_data.iloc[1:].reset_index(drop=True)
# Construire la liste des colonnes réorganisées
        reordered_columns = []

        # Ajouter la colonne 'Date' en premier si elle existe
        if 'Date' in all_data.columns:
            reordered_columns.append('Date')

        tickers = [col.replace('Price_', '') for col in all_data.columns if col.startswith('Price_') and not col.startswith('Price_OpenDate_')]

        # Ajouter les colonnes associées à chaque ticker
        for ticker in tickers:
            reordered_columns.extend([f'Price_{ticker}', f'LogReturn_{ticker}'])

        # Vérifier les colonnes manquantes
        missing_columns = [col for col in reordered_columns if col not in all_data.columns]
        if missing_columns:
            print("Colonnes manquantes :", missing_columns)

        # Réorganiser uniquement les colonnes existantes
        all_data = all_data[[col for col in reordered_columns if col in all_data.columns]]
        print("Colonnes réorganisées avec succès.")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        all_data.to_csv(temp_file.name, index=False)


        # Enregistrer le chemin du fichier temporaire dans la session
        session['all_data'] = temp_file.name

        temps_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        portfolio_df.to_csv(temps_file.name, index=False)
        session['portfolio_df'] = temps_file.name


        # Conversion en format JSON
        return jsonify({
            'all_data': all_data.to_dict(orient='records'),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500





@app.route('/Visualization')
def visualization():
    # --- Chargement des données ---
    get_enrich_portfolio_data()
    all_data_file = session.get('all_data')
    if all_data_file is None:
        print("Aucun fichier de données trouvé dans la session.")
        return jsonify({"error": "Aucun fichier de données trouvé dans la session."}), 400
    if not os.path.exists(all_data_file):
        return jsonify({"error": f"Le fichier spécifié n'existe pas: {all_data_file}"}), 400

    all_data = pd.read_csv(all_data_file)
    print("Fichier de données :", all_data_file)
    
    # Filtrer les colonnes de rendements logarithmiques
    log_return_columns = [col for col in all_data.columns if col.startswith('LogReturn_')]
    if not log_return_columns:
        return jsonify({"error": "Aucune colonne de rendements logarithmiques trouvée."}), 400
    print(log_return_columns)
    # Calcul des matrices de covariance et de corrélation
    covariance_matrix = all_data[log_return_columns].cov()
    correlation_matrix = all_data[log_return_columns].corr()

    # --- Chargement des informations du portefeuille ---
    portfolio_infos_file = session.get('enriched_portfolio_df')
    if portfolio_infos_file is None:
        print("Aucun fichier portfolio_infos trouvé dans la session.")
        return jsonify({"error": "Aucun fichier portfolio_infos trouvé dans la session."}), 400
    if not os.path.exists(portfolio_infos_file):
        return jsonify({"error": f"Le fichier spécifié n'existe pas: {portfolio_infos_file}"}), 400

    portfolio_infos_df = pd.read_csv(portfolio_infos_file)
    print (portfolio_infos_df)
    # --- Construction du DataFrame résumé (modélisation des positions) ---
    # On ne conserve que les actions pour lesquelles la colonne LogReturn existe
    stocks = portfolio_infos_df['StockID'].values
    print(stocks)
    valid_stocks = []
    mean_log_returns = []
    volatilities = []
    for stock in stocks:
        col_name = f"LogReturn_{stock}"
        if col_name in all_data.columns:
            valid_stocks.append(stock)
            mean_log_returns.append(all_data[col_name].mean())
            volatilities.append(all_data[col_name].std())
    if not valid_stocks:
        return jsonify({"error": "Aucune action valide trouvée dans les données."}), 400

    summary_df = pd.DataFrame({
        'StockID': valid_stocks,
        'MeanLogReturn': mean_log_returns,
        'Volatility': volatilities
    })
    print (summary_df)
    # Fonction pour annualiser le rendement logarithmique moyen
    def annualize_mean_log_return(row):
        open_date = portfolio_infos_df.loc[portfolio_infos_df['StockID'] == row['StockID'], 'OpenDate'].values
        if len(open_date) == 0 or pd.isna(open_date[0]):
            return None
        open_date = pd.to_datetime(open_date[0])
        days_since_open = (datetime.now() - open_date).days
        annualization_factor = 8760 if days_since_open <= 146 else 252
        return row['MeanLogReturn'] * annualization_factor

    summary_df['AnnualizedMeanLogReturn'] = summary_df.apply(annualize_mean_log_return, axis=1)

    # Convertir les DataFrames en tableaux HTML pour le front-end
    summary_table = summary_df.to_html(classes="table table-bordered table-hover", index=False)
    covariance_table = covariance_matrix.to_html(classes="table table-bordered table-hover")
    correlation_table = correlation_matrix.to_html(classes="table table-bordered table-hover")

    # --- Création des graphiques interactifs avec Plotly ---

    # 1. Nuage de points : Volatilité vs Rendement Annualisé
    scatter_fig = go.Figure()
    scatter_fig.add_trace(go.Scatter(
        x=summary_df['Volatility'],
        y=summary_df['AnnualizedMeanLogReturn'],
        mode='markers+text',
        text=summary_df['StockID'],
        textposition='top center',
        marker=dict(color='blue', size=10, opacity=0.7),
        name='Positions'
    ))
    scatter_fig.update_layout(
        title='Risque (Volatilité) vs Performance (Rendements Annualisés)',
        xaxis_title='Volatilité',
        yaxis_title='Rendement Annualisé',
        template='plotly_white'
    )
    scatter_div = plotly.offline.plot(scatter_fig, output_type='div', include_plotlyjs=False)

    # 2. Heatmap de la matrice de corrélation
    heatmap_corr_fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='rdbu',
        zmin=-1,
        zmax=1,
        hovertemplate='Corr: %{z:.2f}<extra></extra>'
    ))
    heatmap_corr_fig.update_layout(
        title='Matrice de Corrélation des Rendements Logarithmiques',
        template='plotly_white'
    )
    heatmap_corr_div = plotly.offline.plot(heatmap_corr_fig, output_type='div', include_plotlyjs=False)

    # 3. Heatmap de la matrice de covariance
    heatmap_cov_fig = go.Figure(data=go.Heatmap(
        z=covariance_matrix.values,
        x=covariance_matrix.columns,
        y=covariance_matrix.index,
        colorscale='Viridis',
        hovertemplate='Cov: %{z:.6f}<extra></extra>'
    ))
    heatmap_cov_fig.update_layout(
        title='Matrice de Covariance des Rendements Logarithmiques',
        template='plotly_white'
    )
    heatmap_cov_div = plotly.offline.plot(heatmap_cov_fig, output_type='div', include_plotlyjs=False)

    # 4. Frontière Efficiente et Capital Market Line (CML)
    # Préparer les données pour l'optimisation
    mean_returns_array = summary_df['MeanLogReturn'].values
    print(mean_returns_array)
    cov_columns = [f"LogReturn_{stock}" for stock in valid_stocks]
    cov_matrix_array = covariance_matrix.loc[cov_columns, cov_columns].values
    num_assets = len(mean_returns_array)
    print(num_assets)
    def portfolio_performance(weights, mean_returns, cov_matrix):
        ret = np.dot(weights, mean_returns)
        risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return ret, risk

    def minimize_volatility(weights, mean_returns, cov_matrix, target_return):
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: np.dot(w, mean_returns) - target_return}
        ]
        bounds = [(0, 1) for _ in range(num_assets)]
        result = minimize(
            lambda w: portfolio_performance(w, mean_returns, cov_matrix)[1],
            x0=np.ones(num_assets) / num_assets,
            constraints=constraints,
            bounds=bounds,
            method='SLSQP'
        )
        return result

    target_returns = np.linspace(np.nanmin(mean_returns_array), np.nanmax(mean_returns_array), 50)
    efficient_portfolios = []
    for target in target_returns:
        result = minimize_volatility(np.ones(num_assets) / num_assets, mean_returns_array, cov_matrix_array, target)
        if result.success:
            efficient_portfolios.append(portfolio_performance(result.x, mean_returns_array, cov_matrix_array))
    efficient_returns = [pf[0] for pf in efficient_portfolios]
    efficient_risks = [pf[1] for pf in efficient_portfolios]

    efficient_fig = go.Figure()
    efficient_fig.add_trace(go.Scatter(
        x=efficient_risks,
        y=efficient_returns,
        mode='lines',
        name='Frontière Efficiente',
        line=dict(color='blue')
    ))
    efficient_fig.add_trace(go.Scatter(
        x=summary_df['Volatility'],
        y=summary_df['MeanLogReturn'],
        mode='markers+text',
        text=summary_df['StockID'],
        textposition='top center',
        marker=dict(color='red', size=8),
        name='Actifs Individuels'
    ))
    
    # --- Calcul du portefeuille tangent et de la CML ---
    risk_free_rate = 0.00005 # à ajuster selon le contexte
    # Fonction pour optimiser (maximiser) le Sharpe ratio (en minimisant son négatif)
    def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
        ret, risk = portfolio_performance(weights, mean_returns, cov_matrix)
        return -(ret - risk_free_rate) / risk

    constraints_tan = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds_tan = [(0, 1) for _ in range(num_assets)]
    initial_guess = np.ones(num_assets) / num_assets
    tan_result = minimize(
        neg_sharpe_ratio,
        x0=initial_guess,
        args=(mean_returns_array, cov_matrix_array, risk_free_rate),
        method='SLSQP',
        bounds=bounds_tan,
        constraints=constraints_tan
    )
    print(f"Nombre de portefeuilles générés : {len(efficient_portfolios)}")
    print(f"Nombre de rendements cibles : {len(target_returns)}")

    if tan_result.success:
        tan_weights = tan_result.x
        tan_return, tan_risk = portfolio_performance(tan_weights, mean_returns_array, cov_matrix_array)
        tan_sharpe = (tan_return - risk_free_rate) / tan_risk

        # Construction de la CML : ligne partant du taux sans risque et passant par le portefeuille tangent
        max_risk = max(efficient_risks) * 1.2  # étendre légèrement l'axe des risques
        risk_range = np.linspace(0, max_risk, 100)
        cml_returns = risk_free_rate + tan_sharpe * risk_range

        efficient_fig.add_trace(go.Scatter(
            x=risk_range,
            y=cml_returns,
            mode='lines',
            name='Capital Market Line',
            line=dict(color='green', dash='dash')
        ))

        # Optionnel : ajouter le point du portefeuille tangent
        efficient_fig.add_trace(go.Scatter(
            x=[tan_risk],
            y=[tan_return],
            mode='markers',
            name='Portefeuille Tangent',
            marker=dict(color='green', size=12, symbol='diamond')
        ))

    efficient_fig.update_layout(
        title='Frontière Efficiente, Actifs Individuels et Capital Market Line',
        xaxis_title='Volatilité (Risque)',
        yaxis_title='Rendement',
        template='plotly_white'
    )
    efficient_div = plotly.offline.plot(efficient_fig, output_type='div', include_plotlyjs=False)

    # --- Calcul des métriques du portefeuille ---
    if 'PositionValue' in portfolio_infos_df.columns:
        total_value = portfolio_infos_df['PositionValue'].sum()
    else:
        total_value = "N/A"
    portfolio_metrics = {
        "Total Portfolio Value": total_value,
        "Average Return": round(summary_df["MeanLogReturn"].mean(), 4),
        "Average Volatility": round(summary_df["Volatility"].mean(), 4)
    }


    price_fig = go.Figure()

    for idx, column in enumerate(all_data.columns):
        if column.startswith("Price_"):
            stock_id = column.replace("Price_", "")
            
            # Tracer l'évolution complète du prix pour ce stock
            price_fig.add_trace(go.Scatter(
                x=all_data['Date'],
                y=all_data[column],
                mode='lines',
                name=stock_id,
                line=dict(width=2)
            ))
            
            # Récupérer la date d'ouverture pour ce stock dans portfolio_infos_df
            open_date_str = portfolio_infos_df.loc[portfolio_infos_df['StockID'] == stock_id, 'OpenDate'].values[0]
            open_date = pd.to_datetime(open_date_str)
            
            # Convertir la colonne "Date" en tableau NumPy de type datetime64
            all_dates = np.array(all_data['Date'], dtype='datetime64[ns]')
            # Convertir la date d'ouverture en objet NumPy datetime64
            open_date_np = np.datetime64(open_date)
            
            # Trouver l'indice du jour de trading le plus proche de la date d'ouverture
            closest_idx = (np.abs(all_dates - open_date_np)).argmin()
            
            # Extraire la date et le prix correspondants à cet indice
            closest_date = all_data['Date'].iloc[closest_idx]
            closest_price = all_data[column].iloc[closest_idx]
            
            # Ajouter un marqueur rouge à la date d'ouverture (ou la date de trading la plus proche)
            price_fig.add_trace(go.Scatter(
                x=[closest_date],
                y=[closest_price],
                mode='markers',
                marker=dict(color='red', size=10, symbol='circle'),
                name=f"Début {stock_id}",
                showlegend=False
            ))


    price_fig.update_layout(
        title={'text': "Évolution des prix des actifs", 'x': 0.5},
        xaxis_title="Date",
        yaxis_title="Prix",
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    price_div = plotly.offline.plot(price_fig, output_type='div', include_plotlyjs=False)
    print("Price Graph Div:", price_div[:200])



    # --- Envoi de toutes les informations au template ---
    return render_template('Visualization.html',
                           summary_table=summary_table,
                           covariance_table=covariance_table,
                           correlation_table=correlation_table,
                           scatter_div=scatter_div,
                           heatmap_corr_div=heatmap_corr_div,
                           heatmap_cov_div=heatmap_cov_div,
                           efficient_div=efficient_div,
                           portfolio_metrics=portfolio_metrics,
                           price_div=price_div)


@app.route('/delto') 
def delto():
    return render_template('Hedging.html')

@app.route('/api/delta', methods=['GET', 'POST'])
def delta():
    try:
        # Recevoir les données JSON envoyées depuis le frontend
        data = request.get_json()

        # Vérifier que les données sont bien un tableau non vide
        if not data or not isinstance(data, list):
            return jsonify({"error": "Données invalides ou vides. Un tableau JSON est attendu."}), 400
        
        # Convertir les données reçues en un DataFrame
        hedginginfo = pd.DataFrame(data)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')
        # Sauvegarder le DataFrame dans ce fichier
        hedginginfo.to_csv(temp_file.name, index=False)

        # Stocker le chemin du fichier dans la session
        session['hedging_info'] = temp_file.name




        # Vérifier que le DataFrame n'est pas vide
        if hedginginfo.empty:
            return jsonify({"error": "Le DataFrame créé est vide. Vérifiez les données envoyées."}), 400

        # Retourner une réponse de succès
        return jsonify({"message": "Données du portefeuille ajoutées avec succès!"}), 200 

    except Exception as e:
        # Gestion des erreurs avec message détaillé
        return jsonify({"error": f"Erreur lors de l'ajout des données : {str(e)}"}), 500


                           



@app.route('/deltaBlackandSholes')
def deltaBlackandSholes():



    # Récupérer le chemin du fichier stocké dans la session
    hedging_info = session.get('hedging_info', None)

    if hedging_info is None:
        print("Aucun fichier de données trouvé dans la session.")
        return jsonify({"error": "Aucun fichier de données trouvé dans la session."}), 400
    if not os.path.exists(hedging_info):
        return jsonify({"error": f"Le fichier spécifié n'existe pas: {hedging_info}"}), 400
    hedging_info = pd.read_csv(hedging_info)  # Si c'est un CSV, sinon utiliser pd.read_excel()

    # Vérifier si le DataFrame est correctement chargé
    print("DataFrame chargé avec succès. Aperçu des premières lignes :")
    print(hedging_info.head())  # Log des premières lignes du DataFrame
    begin_period = datetime.strptime(hedging_info['HedgingBeginingPeriod'][0], "%Y-%m-%d")
    end_period = datetime.strptime(hedging_info['HedgingEndingPeriod'][0], "%Y-%m-%d")

    # Liste des tickers à traiter
    tickers = [
        "AAPL", "GOOGL", "AMZN", "MSFT", "TSLA", "NFLX", "META",
        "NVDA", "AMD", "BA", "DIS", "IBM", "V", "JNJ", "TSM", "GOOG",
        "MCD", "WMT"]

    # Liste pour stocker toutes les options
    all_options = []

    # Parcourir chaque ticker et récupérer les options
    for ticker in tickers:
        asset = yf.Ticker(ticker)
        last_price = asset.history(period="1mo")['Close'].iloc[-1]

        # Obtenir les dates d'expiration disponibles
        expiration_dates = asset.options

        # Vérifier si des dates d'expiration sont disponibles
        if expiration_dates:
            for selected_expiration in expiration_dates:
                # Convertir la date d'expiration au format datetime
                expiration_date = datetime.strptime(selected_expiration, "%Y-%m-%d")

                # Vérifier si la date d'expiration se situe dans la période de couverture
                if begin_period <= expiration_date <= end_period:
                    # Calculer le temps restant jusqu'à l'échéance en années
                    current_date = datetime.today()
                    time_to_expiration = (expiration_date - current_date).days / 365  # Convertir en années

                    # Obtenir les options pour cette date d'expiration
                    options_chain = asset.option_chain(selected_expiration)
                    calls = options_chain.calls
                    puts = options_chain.puts

                    # Construire la liste des options pour chaque ticker
                    options = []
                    for _, row in calls.iterrows():
                        options.append({
                            'name': f"Call {ticker} Strike {row['strike']}",
                            'strike': row['strike'],
                            'cost': row['lastPrice'],
                            'time_to_expiration': time_to_expiration,
                            'expiration_date': selected_expiration,  # Ajouter la date d'expiration
                            'last_price': last_price,  # Ajouter le dernier prix de l'action
                            'open_interest': row['openInterest'],  # Ajouter l'intérêt ouvert (quantité d'options disponibles)
                            'impliedVolatility': row['impliedVolatility']



                        })

                    for _, row in puts.iterrows():
                        options.append({
                            'name': f"Put {ticker} Strike {row['strike']}",
                            'strike': row['strike'],
                            'cost': row['lastPrice'],
                            'time_to_expiration': time_to_expiration,
                            'expiration_date': selected_expiration,  # Ajouter la date d'expiration
                            'last_price': last_price,  # Ajouter le dernier prix de l'action
                            'open_interest': row['openInterest'],  # Ajouter l'intérêt ouvert (quantité d'options disponibles)
                            'impliedVolatility': row['impliedVolatility']


                        })

                    # Ajouter les options du ticker à la liste globale
                    all_options.extend(options)
        else:
            print(f"Pas de dates d'expiration disponibles pour {ticker}")

    # Créer un DataFrame avec les options
    options_df = pd.DataFrame(all_options)

    # Afficher le DataFrame
    print(options_df)



    # Télécharger le taux du Trésor US à 10 ans
    risk_free_rate_data = yf.download("^TNX", period="1mo", interval="1d")
    r = risk_free_rate_data["Close"].iloc[-1] / 100  # Convertir en décimal

    def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
        """
        Calcule le delta d'une option européenne avec la formule de Black-Scholes.

        :param S: Prix de l'actif sous-jacent (S₀)
        :param K: Prix d'exercice (strike)
        :param T: Temps jusqu'à l'échéance (en années)
        :param r: Taux d'intérêt sans risque (en décimal)
        :param sigma: Volatilité implicite (en décimal)
        :param option_type: Type d'option ('call' ou 'put')
        :return: Delta de l'option
        """
        # Calcul de d1 dans la formule de Black-Scholes
        d1 = (np.log(S / K) + (r + (sigma**2) / 2) * T) / (sigma * np.sqrt(T))

        # Calcul du delta en fonction du type d'option
        if option_type == 'call':
            return si.norm.cdf(d1)  # N(d1) pour un call
        elif option_type == 'put':
            return si.norm.cdf(d1) - 1  # N(d1) - 1 pour un put
        else:
            raise ValueError("Le type d'option doit être 'call' ou 'put'.")

    # Exemple de taux d'intérêt sans risque et volatilité (vous pouvez ajuster)
    options_df['impliedVolatility'] = options_df['impliedVolatility'].astype(float)
    options_df = options_df[options_df['impliedVolatility'] != 1]

    options_df = options_df[options_df['impliedVolatility'] > 0.000011]

    # Parcourir le DataFrame et calculer le delta pour chaque option
    def calculate_option_deltas(options_df):
        deltas = []

        for index, row in options_df.iterrows():
            S = row['last_price']  # Le prix actuel de l'actif sous-jacent
            K = row['strike']  # Le prix d'exercice (strike)
            sigma = row['impliedVolatility']
            T = row['time_to_expiration']  # Le temps jusqu'à l'échéance (en années)
            option_type = 'call' if 'Call' in row['name'] else 'put'  # Déterminer le type d'option

            # Calculer le delta
            delta = black_scholes_delta(S, K, T, r, sigma, option_type)
            deltas.append(delta)

        # Ajouter la colonne 'delta' au DataFrame
        options_df['delta'] = deltas
        return options_df

    # Appliquer le calcul des deltas sur le DataFrame options_df
    options_df = calculate_option_deltas(options_df)

    # Afficher le DataFrame avec la colonne 'delta'
    print(options_df)
    options_df['potential_coverage'] = options_df['delta'] * options_df['last_price']
# 1️⃣ Convertir la date cible en `datetime`
    hedging_ending_period = hedging_info['HedgingEndingPeriod'][0]  # Exemple : '2025-01-21'

    if isinstance(hedging_ending_period, str):
        target_date = datetime.strptime(hedging_ending_period, "%Y-%m-%d")
    elif isinstance(hedging_ending_period, datetime):
        target_date = hedging_ending_period
    else:
        raise ValueError("Le format de 'HedgingEndingPeriod' n'est pas reconnu.")

    # 2️⃣ Date actuelle
    current_date = datetime.now()

    # 3️⃣ Calcul du temps restant en années
    days_to_end = (target_date - current_date).days
    years_to_end = days_to_end / 365.0

    print(f"🟢 Nombre d'années restantes : {years_to_end:.4f}")

    # 4️⃣ Convertir `time_to_expiration` en datetime puis en années restantes
    options_df['time_to_expiration'] = pd.to_datetime(options_df['time_to_expiration'], format="%Y-%m-%d")
    options_df['time_to_expiration_years'] = (options_df['time_to_expiration'] - current_date).dt.days / 365.0

    # 5️⃣ Filtrer les options selon `years_to_end`
    tolerance = 0.01  # 1% de tolérance (~3-4 jours)
    options_df = options_df[
        (options_df['time_to_expiration_years'] >= years_to_end - tolerance) &
        (options_df['time_to_expiration_years'] <= years_to_end + tolerance)
    ]

    # Affichage du DataFrame filtré
    print(f"🟢 Options filtrées ({len(options_df)} résultats) :\n", options_df)
    options_df['delta'] = options_df['delta'].astype(float)
    tolerance2 = 1e-6
    print(f"pORTFOLIO 2 : {options_df}")

    # Filtrer les valeurs de delta en dehors de l'intervalle [1 - tolérance, 1 + tolérance]
    options_df = options_df[
        ~((options_df['delta'] >= 1 - tolerance2) & (options_df['delta'] <= 1 + tolerance2))
    ]
    # Convertir en float au cas où ce n'est pas déjà fait
    options_df['potential_coverage'] = pd.to_numeric(options_df['potential_coverage'], errors='coerce')
    print(f"pORTFOLIO 3 : {options_df}")

    # Appliquer la valeur absolue
    options_df['potential_coverage'] = options_df['potential_coverage'].abs()
    print(f"pORTFOLIO 4 : {options_df}")

    options_df['Type'] = options_df['name'].str.split().str[0]
    print(f"pORTFOLIO 5 : {options_df}")

    print(f"pORTFOLIO FINAL : {options_df}")


    # 🔹 1. Distribution des deltas
    plt.figure(figsize=(8, 5))
    sns.histplot(options_df['delta'], bins=20, kde=True)
    plt.title("Distribution des deltas des options")
    plt.xlabel("Valeur du delta")
    plt.ylabel("Nombre d'options")
    plt.grid(True)

    # Sauvegarde de l'image en base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    delta_dist_plot = base64.b64encode(img.getvalue()).decode()



    # 🔹 Retourner la page HTML avec les données et les graphiques
    return render_template('visu_hedging.html',
                           options_df=options_df,
                           hedging_info=hedging_info,
                           delta_dist_plot=delta_dist_plot
                           )






@app.route('/export_to_xlsx')
def export_to_xlsx():
    try:
        # Récupérer le chemin du fichier stocké dans la session
        all_data_file = session.get('all_data', None)

        if all_data_file is None:
            print("Aucun fichier de données trouvé dans la session.")
            return jsonify({"error": "Aucun fichier de données trouvé dans la session."}), 400
        if not os.path.exists(all_data_file):
            return jsonify({"error": f"Le fichier spécifié n'existe pas: {all_data_file}"}), 400
        all_data = pd.read_csv(all_data_file)  # Si c'est un CSV, sinon utiliser pd.read_excel()

        # Vérifier si le DataFrame est correctement chargé
        print("DataFrame chargé avec succès. Aperçu des premières lignes :")
        print(all_data.head())  # Log des premières lignes du DataFrame

        # Spécifie un chemin pour le fichier Excel
        file_path = '/Historical_LogReturns.xlsx'  # Le chemin du fichier temporaire
        print(f"Création du fichier Excel à l'emplacement: {file_path}")

        # Générer le fichier Excel
        all_data.to_excel(file_path, index=False)
        print(f"Fichier Excel généré avec succès à l'emplacement: {file_path}")

        # Renvoie le fichier Excel pour le téléchargement
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        # Log des erreurs si une exception se produit
        print(f"Erreur lors de la génération du fichier Excel: {str(e)}")
        return jsonify({"error": f"Erreur lors de la génération du fichier Excel: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
