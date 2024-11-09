import yfinance as yf
import pandas as pd
import numpy as np
import logging

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_crossovers():
    """
    Pobiera dane BTC-USD od 2024-01-01, oblicza 50-dniową i 200-dniową średnią kroczącą,
    identyfikuje punkty przecięcia i zwraca listę dat tych przecięć.
    
    Returns:
        list: Lista dat przecięć w formacie 'YYYY-MM-DD'.
    """
    try:
        # Step 1: Retrieve BTC-USD data from 2024-01-01
        logger.info("Pobieranie danych BTC-USD od 2024-01-01")
        btc_data = yf.download('BTC-USD', start='2024-01-01', progress=False)
        logger.info(f"Pobrano dane: {btc_data.shape[0]} wierszy, {btc_data.shape[1]} kolumn")
        
        if btc_data.empty:
            logger.error("Brak danych po pobraniu.")
            return []
        
        # Sprawdzenie kolumn
        logger.info(f"Dostępne kolumny: {btc_data.columns.tolist()}")
        
        # Step 2: Calculate 50-day and 200-day rolling mean (moving averages)
        if 'Close' not in btc_data.columns:
            logger.error("Brak kolumny 'Close' w danych")
            return []
        
        btc_data['50-day MA'] = btc_data['Close'].rolling(window=50).mean()
        btc_data['200-day MA'] = btc_data['Close'].rolling(window=200).mean()
        logger.info("Obliczono 50-dniową i 200-dniową średnią kroczącą.")
        
        # Step 3: Drop rows where either 50-day or 200-day MA is NaN
        if '50-day MA' not in btc_data.columns or '200-day MA' not in btc_data.columns:
            logger.error("Brak kolumn '50-day MA' lub '200-day MA'")
            return []
        
        btc_data.dropna(subset=['50-day MA', '200-day MA'], inplace=True)
        logger.info(f"Dane po usunięciu NaN: {btc_data.shape[0]} wierszy")
        
        if btc_data.empty:
            logger.error("Brak danych po usunięciu NaN.")
            return []
        
        # Step 4: Calculate the difference between the two moving averages
        btc_data['MA Difference'] = btc_data['50-day MA'] - btc_data['200-day MA']
        logger.info("Obliczono różnicę między średnimi kroczącymi.")
        
        # Step 5: Find the points where the sign of the difference changes (potential crossing points)
        btc_data['Signal'] = np.sign(btc_data['MA Difference'])
        btc_data['Crossover'] = btc_data['Signal'].diff()
        logger.info("Zidentyfikowano potencjalne punkty przecięcia.")
        
        # Step 6: Filter crossovers and ensure the means are close enough to be considered a crossover
        threshold = 500  # Set a threshold for considering it a crossover
        crossovers = btc_data[(btc_data['Crossover'] != 0) & (btc_data['MA Difference'].abs() < threshold)]
        logger.info(f"Znaleziono {crossovers.shape[0]} punktów przecięcia spełniających kryteria.")
        
        # Extract dates of crossovers
        crossover_dates = crossovers.index.strftime('%Y-%m-%d').tolist()
        logger.info(f"Daty przecięć: {crossover_dates}")
        
        return crossover_dates
    except Exception as e:
        logger.exception("Wystąpił błąd w funkcji find_crossovers")
        return []
