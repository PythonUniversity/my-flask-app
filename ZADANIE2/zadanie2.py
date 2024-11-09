import yfinance as yf
import pandas as pd
import numpy as np

def find_crossovers():
    """
    Pobiera dane BTC-USD od 2024-01-01, oblicza 50-dniową i 200-dniową średnią kroczącą,
    identyfikuje punkty przecięcia i zwraca listę dat tych przecięć.
    
    Returns:
        list: Lista dat przecięć w formacie 'YYYY-MM-DD'.
    """
    # Step 1: Retrieve BTC-USD data from 2024-01-01
    btc_data = yf.download('BTC-USD', start='2024-01-01', progress=False)
    
    # Step 2: Calculate 50-day and 200-day rolling mean (moving averages)
    btc_data['50-day MA'] = btc_data['Close'].rolling(window=50).mean()
    btc_data['200-day MA'] = btc_data['Close'].rolling(window=200).mean()
    
    # Step 3: Drop rows where either 50-day or 200-day MA is NaN
    btc_data.dropna(subset=['50-day MA', '200-day MA'], inplace=True)
    
    # Step 4: Calculate the difference between the two moving averages
    btc_data['MA Difference'] = btc_data['50-day MA'] - btc_data['200-day MA']
    
    # Step 5: Find the points where the sign of the difference changes (potential crossing points)
    btc_data['Signal'] = np.sign(btc_data['MA Difference'])
    btc_data['Crossover'] = btc_data['Signal'].diff()
    
    # Step 6: Filter crossovers and ensure the means are close enough to be considered a crossover
    threshold = 500  # Set a threshold for considering it a crossover
    crossovers = btc_data[(btc_data['Crossover'] != 0) & (btc_data['MA Difference'].abs() < threshold)]
    
    # Extract dates of crossovers
    crossover_dates = crossovers.index.strftime('%Y-%m-%d').tolist()
    
    return crossover_dates

def calculate_total_btc_traded():
    """
    Pobiera dane BTC-USD z ostatnich 5 dni z interwałem godzinowym,
    oblicza ilość BTC handlowanych w ostatnich 6 pełnych godzinach
    i zwraca tę wartość jako liczbę całkowitą.
    
    Returns:
        int: Łączna ilość BTC handlowanych w ostatnich 6 pełnych godzinach.
    """
    # Step 1: Retrieve BTC-USD data with hourly interval for the last 5 days
    btc_data = yf.download('BTC-USD', period='5d', interval='1h', progress=False)
    
    # Step 2: Filter the last 6 full hours of data
    last_6_hours_data = btc_data.tail(6).copy()  # Aby uniknąć SettingWithCopyWarning
    
    # Step 3: Calculate the number of BTC traded per hour
    # Volume jest w USD, a Close to cena 1 BTC w USD, więc Volume / Close daje ilość BTC
    last_6_hours_data['BTC Traded'] = last_6_hours_data['Volume'] / last_6_hours_data['Close']
    
    # Step 4: Sum the BTC traded in the last 6 hours
    total_btc_traded = last_6_hours_data['BTC Traded'].sum()
    
    return int(total_btc_traded)

if __name__ == '__main__':
    # Wywołanie funkcji i uzyskanie wyników
    crossover_dates = find_crossovers()
    total_traded = calculate_total_btc_traded()
    
    # Drukowanie wyników w żądanym formacie
    print(" ".join(crossover_dates))
    print(total_traded)
