# dashboard/engines/forecaster.py

# India real estate CAGR by city tier (historical average)
CITY_CAGR = {
    # Metro — highest appreciation
    'Mumbai': 0.10, 'New Delhi': 0.10, 'Bangalore': 0.11,
    'Chennai': 0.09, 'Hyderabad': 0.10, 'Kolkata': 0.08,
    'Pune': 0.10, 'Ahmedabad': 0.09,
    # Tier 2 — moderate appreciation
    'Surat': 0.08, 'Jaipur': 0.08, 'Noida': 0.09,
    'Gurgaon': 0.09, 'Indore': 0.07, 'Bhopal': 0.07,
    'Lucknow': 0.07, 'Patna': 0.06, 'Kochi': 0.08,
    'Trivandrum': 0.07, 'Coimbatore': 0.07, 'Nagpur': 0.07,
    # Tier 3 — lower appreciation
    'Mysore': 0.06, 'Mangalore': 0.06, 'Ranchi': 0.05,
    'Jamshedpur': 0.05, 'Gaya': 0.05, 'Silchar': 0.04,
    'Bilaspur': 0.05, 'Raipur': 0.06, 'Dehradun': 0.07,
    'Haridwar': 0.06, 'Guwahati': 0.06, 'Durgapur': 0.05,
    'Bhubaneswar': 0.07, 'Cuttack': 0.06, 'Vijayawada': 0.07,
    'Vishakhapatnam': 0.07, 'Warangal': 0.06, 'Jodhpur': 0.06,
    'Amritsar': 0.06, 'Ludhiana': 0.06, 'Faridabad': 0.07,
    'Dwarka': 0.08,
}

DEFAULT_CAGR = 0.07  # fallback for unknown cities


def get_forecast(predicted_price, city, availability_status):
    """
    Forecast property price at 1, 3, 5 years.
    Uses city-tier CAGR + availability adjustment.

    Formula: Future Price = P × (1 + CAGR)^n
    """
    cagr = CITY_CAGR.get(city, DEFAULT_CAGR)

    # Under construction adds slight premium on completion
    if availability_status == 'Under_Construction':
        cagr += 0.01  # 1% extra appreciation on completion

    forecast_1yr = round(predicted_price * (1 + cagr) ** 1, 2)
    forecast_3yr = round(predicted_price * (1 + cagr) ** 3, 2)
    forecast_5yr = round(predicted_price * (1 + cagr) ** 5, 2)

    appreciation_1yr = round(((forecast_1yr - predicted_price) / predicted_price) * 100, 1)
    appreciation_3yr = round(((forecast_3yr - predicted_price) / predicted_price) * 100, 1)
    appreciation_5yr = round(((forecast_5yr - predicted_price) / predicted_price) * 100, 1)

    return {
        'current':          predicted_price,
        'cagr_percent':     round(cagr * 100, 1),
        'forecast_1yr':     forecast_1yr,
        'forecast_3yr':     forecast_3yr,
        'forecast_5yr':     forecast_5yr,
        'appreciation_1yr': appreciation_1yr,
        'appreciation_3yr': appreciation_3yr,
        'appreciation_5yr': appreciation_5yr,
        'city':             city,
    }