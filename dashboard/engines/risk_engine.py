# dashboard/engines/risk_engine.py

import numpy as np

def calculate_risk_score(
    age_of_property,
    crime_index,
    availability_status,
    floor_ratio,
    infra_growth_score,
    population_density
):
    """
    Calculate risk score 0-10 and category.
    
    Risk Factors (from task doc):
    - Crime Index
    - Property Age
    - Market Volatility (proxied by availability + floor ratio)
    - Demand Trends (proxied by infra score + population density)
    """

    # 1. Age Risk — older property = higher risk
    age_risk = np.clip(age_of_property / 35, 0, 1)  # max age in dataset is 35

    # 2. Crime Risk — already 1-10, normalize to 0-1
    crime_risk = np.clip(crime_index / 10, 0, 1)

    # 3. Market Volatility Risk
    # Underconstruction = higher risk than ready to move
    availability_risk = 0.8 if availability_status == 'Under_Construction' else 0.2
    # Very high or very low floor = slightly riskier
    floor_risk = abs(floor_ratio - 0.5)  # 0 = middle floor (safest), 0.5 = top/ground

    volatility_risk = (availability_risk * 0.7 + floor_risk * 0.3)

    # 4. Demand Trend Risk — low infra + low density = low demand = higher risk
    infra_norm = np.clip(infra_growth_score / 10, 0, 1)
    density_norm = np.clip(population_density / 26903, 0, 1)  # max density in dataset
    demand_risk = 1 - (infra_norm * 0.5 + density_norm * 0.5)  # inverse — low demand = high risk

    # Weighted final risk score
    risk_score = (
        crime_risk    * 0.30 +
        age_risk      * 0.25 +
        volatility_risk * 0.25 +
        demand_risk   * 0.20
    )

    # Scale to 0-10
    risk_score = round(float(risk_score * 10), 2)

    # Category
    if risk_score <= 3.3:
        category = 'Low'
        color = 'green'
    elif risk_score <= 6.6:
        category = 'Medium'
        color = 'orange'
    else:
        category = 'High'
        color = 'red'

    return {
        'risk_score': risk_score,
        'risk_category': category,
        'color': color,
        'breakdown': {
            'Crime Risk':     round(crime_risk * 10, 2),
            'Age Risk':       round(age_risk * 10, 2),
            'Volatility Risk': round(volatility_risk * 10, 2),
            'Demand Risk':    round(demand_risk * 10, 2),
        }
    }