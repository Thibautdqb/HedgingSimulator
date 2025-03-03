
@app.route('/blackandscholesdeltas')
def blackandscholesdeltas():
        


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
        hedging_ending_period = user_responses['HedgingEndingPeriod'][0]  # Exemple : '2025-01-21'

        # Convertir la date cible en objet datetime (si nécessaire)
        if isinstance(hedging_ending_period, str):
            target_date = datetime.strptime(hedging_ending_period, "%Y-%m-%d")
        elif isinstance(hedging_ending_period, datetime):
            target_date = hedging_ending_period
        else:
            raise ValueError("Le format de 'HedgingEndingPeriod' n'est pas reconnu.")

        # Date actuelle
        current_date = datetime.now()

        # Calculer le nombre de jours jusqu'à la fin de la période
        days_to_end = (target_date - current_date).days

        # Convertir en années
        years_to_end = days_to_end / 365.0
        print(years_to_end)
        tolerance = 1e-6

        # Filtrer les options avec une comparaison approximative
        options_df = options_df[
            (options_df['time_to_expiration'] >= years_to_end - tolerance) &
            (options_df['time_to_expiration'] <= years_to_end + tolerance)
        ]
        options_df['delta'] = options_df['delta'].astype(float)
        tolerance2 = 1e-2

        # Filtrer les valeurs de delta en dehors de l'intervalle [1 - tolérance, 1 + tolérance]
        options_df = options_df[
            ~((options_df['delta'] >= 1 - tolerance2) & (options_df['delta'] <= 1 + tolerance2))
        ]
        # Convertir en float au cas où ce n'est pas déjà fait
        options_df['potential_coverage'] = pd.to_numeric(options_df['potential_coverage'], errors='coerce')

        # Appliquer la valeur absolue
        options_df['potential_coverage'] = options_df['potential_coverage'].abs()

        options_df['Type'] = options_df['name'].str.split().str[0]

        print(options_df)


    return render_template('back_to_modelisation.html',
                           options_df=options_df,
                           user_responses=user_responses)
 

