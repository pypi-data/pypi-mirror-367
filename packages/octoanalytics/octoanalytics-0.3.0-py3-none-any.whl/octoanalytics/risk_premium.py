"""
Classe RiskPremium
------------------
Ce module contient la classe RiskPremium qui regroupe des méthodes pour calculer
différents types de primes de risque dans le domaine de l’énergie, basées sur des
prévisions de consommation, des prix spot et des prix forward.

Fonctionnalités principales :
- Calcul de la prime de risque volume, qui mesure l'impact de l'erreur de prévision
  sur la valeur économique d'un portefeuille d'énergie.
- Calcul de la prime de risque shape, qui évalue le risque lié à la différence entre
  un profil d’achat plat et le profil réel de consommation revendu sur le marché spot.
- Visualisation optionnelle des distributions des primes de risque sous forme de graphiques interactifs.

Auteur : Jean Bertin  
Email : jean.bertin@octopusenergy.fr
"""

from typing import Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class RiskPremium:
    @staticmethod
    def calculate_prem_risk_vol(
        forecast_df: pd.DataFrame,
        spot_df: pd.DataFrame,
        forward_df: pd.DataFrame,
        quantile: int = 70,
        plot_chart: bool = False,
        variability_factor: float = 1.1,
        save_path: Optional[str] = None
    ) -> float:
        """
        Calcule la prime de risque volume à partir des prévisions de consommation, des prix spot et 
        d’un ensemble de prix forward. Cette prime mesure l’impact de l’erreur de prévision sur la valeur 
        économique, en supposant un écart entre consommation réelle et prévision.

        Paramètres :
        -----------
        forecast_df : pd.DataFrame
            Données de consommation et prévisions, contenant :
                - une colonne 'timestamp' (datetime)
                - une colonne 'forecast' (prévisions de consommation en MW)
                - une colonne 'MW' (consommation réalisée en MW)
        spot_df : pd.DataFrame
            Données de prix spot avec les colonnes ['delivery_from', 'price_eur_per_mwh'].
        forward_df : pd.DataFrame
            Liste des prix forward (calendaires ou autres), avec au minimum la colonne ['forward_price'].
        quantile : int, par défaut 70
            Le quantile à extraire (entre 1 et 100) de la distribution des primes calculées.
        plot_chart : bool, par défaut False
            Si True, affiche un graphique interactif de la distribution des primes de risque volume.
        variability_factor : float, par défaut 1.1
            Facteur multiplicatif appliqué à l’erreur de prévision pour simuler une incertitude plus élevée.
        save_path : str, optionnel
            Si défini, sauvegarde le graphique au format HTML à ce chemin.

        Retour :
        -------
        float
            La valeur du quantile demandé (en €/MWh), représentant la prime de risque volume.
        """

        # 1. Conversion des colonnes temporelles en datetime sans timezone
        forecast_df['timestamp'] = pd.to_datetime(forecast_df['timestamp']).dt.tz_localize(None)
        spot_df['delivery_from'] = pd.to_datetime(spot_df['delivery_from']).dt.tz_localize(None)

        # 2. Année de référence basée sur la dernière date de prévision
        latest_date = forecast_df['timestamp'].max()
        latest_year = latest_date.year
        print(f"Using year from latest date: {latest_year} (latest forecast: {latest_date.strftime('%Y-%m-%d')})")

        # 3. Vérification des prix forward
        if forward_df.empty:
            raise ValueError("No forward prices provided.")
        forward_prices = forward_df['forward_price'].tolist()

        # 4. Jointure forecast + spot
        merged_df = pd.merge(
            forecast_df,
            spot_df,
            left_on='timestamp',
            right_on='delivery_from',
            how='inner'
        )
        if merged_df.empty:
            raise ValueError("No data available to merge spot and forecast.")

        # 5. Simulation de l’erreur de prévision (écart entre réel et prévu)
        merged_df['diff_conso'] = (merged_df['MW'] - merged_df['forecast']) * variability_factor
        conso_totale_MWh = merged_df['MW'].sum()
        if conso_totale_MWh == 0:
            raise ValueError("Annual consumption is zero, division not possible.")

        # 6. Calcul de la prime de risque pour chaque prix forward
        premiums = []
        for fwd_price in forward_prices:
            merged_df['diff_price'] = merged_df['price_eur_per_mwh'] - fwd_price
            merged_df['produit'] = merged_df['diff_conso'] * merged_df['diff_price']
            premium = abs(merged_df['produit'].sum()) / conso_totale_MWh
            premiums.append(premium)

        # 7. Visualisation de la distribution (optionnel)
        if plot_chart or save_path:
            premiums_sorted = sorted(premiums)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=premiums_sorted,
                x=list(range(1, len(premiums_sorted) + 1)),
                mode='lines+markers',
                name='Premiums',
                line=dict(color='cyan')
            ))
            fig.update_layout(
                title="Risk premium distribution (volume)",
                xaxis_title="Index (sorted)",
                yaxis_title="Premium (€/MWh)",
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                hovermode='closest'
            )
            if save_path:
                fig.write_html(save_path)
                print(f"Graphique interactif enregistré : {save_path}")
            if plot_chart:
                fig.show()

        # 8. Extraction du quantile demandé
        if not (1 <= quantile <= 100):
            raise ValueError("Quantile must be an integer between 1 and 100.")
        quantile_value = np.percentile(premiums, quantile)
        print(f"Quantile {quantile} risque volume = {quantile_value:.4f} €/MWh")
        return float(quantile_value)


    @staticmethod
    def calculate_prem_risk_shape(
        forecast_df: pd.DataFrame,
        pfc_df: pd.DataFrame,
        spot_df: pd.DataFrame,
        quantile: int = 70,
        plot_chart: bool = False,
        save_path: Optional[str] = None
    ) -> float:
        """
        Calcule la prime de risque de shape à partir d'une prévision de consommation, des prix forward (PFC)
        et des prix spot. Le résultat représente une mesure du risque pris lorsqu'on achète un produit
        à profil plat et qu'on revend au profil réel sur le marché spot.

        Paramètres :
        -----------
        forecast_df : pd.DataFrame
            Données de prévision de consommation, avec :
                - une colonne 'timestamp' (datetime)
                - une colonne 'MW' (consommation réalisée en MW)
                - une colonne 'forecast' (prévisions de consommation en MW)
        pfc_df : pd.DataFrame
            Données de prix forward (PFC) avec les colonnes :
                ['delivery_from', 'forward_price', 'price_date'].
        spot_df : pd.DataFrame
            Données de prix spot avec les colonnes :
                ['delivery_from', 'price_eur_per_mwh'].
        quantile : int, par défaut 70
            Le quantile à extraire de la distribution des coûts shape (en valeur absolue).
        plot_chart : bool, par défaut False
            Si True, affiche un graphique interactif (Plotly) des valeurs triées de prime de shape.
        save_path : str, optionnel
            Si défini, sauvegarde le graphique interactif au format HTML à ce chemin.

        Retour :
        -------
        float
            La valeur du quantile demandé (en €/MWh), mesurant la prime de risque de shape.
        """

        # 1. Prétraitement de la prévision de consommation
        df_conso_prev = forecast_df.copy()
        df_conso_prev = df_conso_prev.rename(columns={'timestamp': 'delivery_from'})
        df_conso_prev['delivery_from'] = pd.to_datetime(df_conso_prev['delivery_from'], utc=True)
        # Suppression des données du 1er avril au 31 octobre (inclus)
        df_conso_prev = df_conso_prev[~df_conso_prev['delivery_from'].dt.month.isin(range(4, 11))]

        # 2. Prétraitement des données PFC
        pfc = pfc_df.copy()
        pfc['delivery_from'] = pd.to_datetime(pfc['delivery_from'], utc=True)

        # 3. Fusion PFC + prévisions conso (jour)
        df = pd.merge(pfc, df_conso_prev[['delivery_from', 'forecast']], on='delivery_from', how='left').dropna()

        # 4. Calcul de la valeur (prix forward * forecast)
        df['value'] = df['forward_price'] * df['forecast']

        # 5. Extraction du mois de livraison et propagation de la date de prix
        df['delivery_month'] = pd.to_datetime(df['delivery_from'].dt.tz_localize(None)).dt.to_period('M')
        df['price_date'] = pfc['price_date']

        # 6. Agrégation mensuelle pour simuler un profil plat
        gb_month = df.groupby(['price_date', 'delivery_month']).agg(
            bl_volume_month=('forecast', 'mean'),
            bl_value_month=('value', 'sum'),
            forward_price_sum_month=('forward_price', 'sum')
        )
        gb_month['bl_value_month'] = gb_month['bl_value_month'] / gb_month['forward_price_sum_month']
        gb_month.reset_index(inplace=True)

        # 7. Prétraitement des données spot
        spot = spot_df.copy()
        spot = spot.rename(columns={'price_eur_per_mwh': 'spot_price'})
        spot['delivery_from'] = pd.to_datetime(spot['delivery_from'], utc=True)

        # 8. Fusion conso + PFC + spot
        df = df.merge(spot[['delivery_from', 'spot_price']], on='delivery_from', how='left').dropna()
        df = df.merge(gb_month, on=['price_date', 'delivery_month'], how='left').dropna()

        # 9. Calcul des volumes résiduels entre profil réel et plat
        df['residual_volume'] = df['forecast'] - df['bl_value_month']
        df['residual_value'] = df['residual_volume'] * df['spot_price']

        # 10. Agrégation mensuelle des coûts shape
        agg = df.groupby(['price_date']).agg(
            residual_value_month=('residual_value', 'sum'),
            conso_month=('forecast', 'sum')
        )
        agg['shape_cost'] = agg['residual_value_month'] / agg['conso_month']
        agg['abs_shape_cost'] = agg['shape_cost'].abs()

        # 11. Affichage graphique (optionnel)
        if plot_chart or save_path:
            sorted_vals = agg['abs_shape_cost'].sort_values().reset_index(drop=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=sorted_vals,
                x=list(range(1, len(sorted_vals) + 1)),
                mode='lines+markers',
                name='Shape Risk',
                line=dict(color='cyan')
            ))
            fig.update_layout(
                title="Shape Risk Distribution",
                xaxis_title="Index (sorted)",
                yaxis_title="€/MWh",
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                hovermode='closest'
            )
            if save_path:
                fig.write_html(save_path)
                print(f"Graphique interactif enregistré : {save_path}")
            if plot_chart:
                fig.show()

        # 12. Extraction du quantile demandé
        if not (1 <= quantile <= 100):
            raise ValueError("Quantile must be un entier entre 1 et 100.")
        quantile_value = np.percentile(agg['abs_shape_cost'], quantile)
        print(f"Quantile {quantile} risque shape = {quantile_value:.4f} €/MWh")
        return float(quantile_value)
