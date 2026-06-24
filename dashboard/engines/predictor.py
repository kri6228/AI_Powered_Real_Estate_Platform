# dashboard/engines/predictor.py

import os

import joblib
import json
import numpy as np
import pandas as pd
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

MODEL_PATH  = os.path.join(BASE_DIR, "models", "best_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "models", "feature_columns.json")

# Load model and features
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

with open(FEATURES_PATH, 'r') as f:
    FEATURES = json.load(f)

# City tier premium (same as feature engineering)
CITY_PREMIUM = {
    'Mumbai': 2.5, 'New Delhi': 2.3, 'Bangalore': 2.0, 'Chennai': 1.9,
    'Hyderabad': 1.8, 'Kolkata': 1.7, 'Pune': 1.6, 'Ahmedabad': 1.5,
    'Surat': 1.4, 'Jaipur': 1.3, 'Noida': 1.4, 'Gurgaon': 1.5,
}

CITY_DENSITY = {
    'Mumbai': 20667, 'Pune': 5800, 'Nagpur': 565,
    'New Delhi': 11297, 'Noida': 3500, 'Gurgaon': 3800,
    'Dwarka': 9000, 'Faridabad': 2900,
    'Bangalore': 4378, 'Mysore': 900, 'Mangalore': 1200,
    'Chennai': 26903, 'Coimbatore': 2000,
    'Hyderabad': 18480, 'Warangal': 850,
    'Vijayawada': 1040, 'Vishakhapatnam': 430,
    'Ahmedabad': 11730, 'Surat': 13600,
    'Jaipur': 6900, 'Jodhpur': 500,
    'Bhopal': 855, 'Indore': 3000,
    'Lucknow': 1815, 'Kolkata': 24252,
    'Durgapur': 1100, 'Kochi': 5798,
    'Trivandrum': 1509, 'Ludhiana': 2200,
    'Amritsar': 1500, 'Jamshedpur': 1200,
    'Ranchi': 740, 'Patna': 1803,
    'Gaya': 480, 'Bhubaneswar': 1600,
    'Cuttack': 2100, 'Raipur': 690,
    'Bilaspur': 420, 'Guwahati': 1540,
    'Silchar': 380, 'Dehradun': 594,
    'Haridwar': 817,
}

STATE_DENSITY = {
    'Andhra Pradesh': 308,  'Assam': 397,       'Bihar': 1102,
    'Chhattisgarh': 189,    'Delhi': 11297,     'Gujarat': 308,
    'Haryana': 573,         'Jharkhand': 414,   'Karnataka': 319,
    'Kerala': 859,          'Madhya Pradesh': 236, 'Maharashtra': 365,
    'Odisha': 269,          'Punjab': 550,      'Rajasthan': 200,
    'Tamil Nadu': 555,      'Telangana': 312,   'Uttar Pradesh': 828,
    'Uttarakhand': 189,     'West Bengal': 1028,
}

# Label encoding maps (must match feature engineering notebook)
CITY_ENCODING = {city: idx for idx, city in enumerate(sorted(CITY_DENSITY.keys()))}
STATE_ENCODING = {state: idx for idx, state in enumerate(sorted(STATE_DENSITY.keys()))}

def build_input(
    city, state, size_sqft, bhk, age,
    floor_no, total_floors, nearby_schools,
    nearby_hospitals, transport, parking,
    security, availability, furnished,
    property_type, facing, owner_type,
    balcony, amenity_count
):
    """Build feature vector from user inputs."""

    # Derived features
    population_density = CITY_DENSITY.get(city, STATE_DENSITY.get(state, 500))
    infra_growth_score = round(
        nearby_schools * 0.30 +
        nearby_hospitals * 0.30 +
        {'High': 10, 'Medium': 5, 'Low': 2}.get(transport, 5) * 0.40, 2
    )
    floor_ratio = round(floor_no / max(total_floors, 1), 2)
    mall_distance = round(np.random.uniform(0.5, 5.0) 
                          if city in CITY_PREMIUM else 
                          np.random.uniform(3.0, 15.0), 1)
    crime_index = round(np.clip(
        np.random.normal(
            loc=3 if population_density < 2000 else 
                5 if population_density < 10000 else 7,
            scale=1.5), 1, 10), 1)

    # Encodings
    transport_enc = {'Low': 1, 'Medium': 2, 'High': 3}.get(transport, 2)
    availability_enc = 1 if availability == 'Ready_to_Move' else 0
    parking_enc = 1 if parking == 'Yes' else 0
    security_enc = 1 if security == 'Yes' else 0
    city_enc = CITY_ENCODING.get(city, 0)
    state_enc = STATE_ENCODING.get(state, 0)

    # One-hot: Property_Type
    prop_apt = 1 if property_type == 'Apartment' else 0
    prop_ind = 1 if property_type == 'Independent House' else 0
    prop_vil = 1 if property_type == 'Villa' else 0

    # One-hot: Furnished_Status
    furn_f  = 1 if furnished == 'Furnished' else 0
    furn_sf = 1 if furnished == 'Semi-furnished' else 0
    furn_uf = 1 if furnished == 'Unfurnished' else 0

    # One-hot: Facing
    face_e = 1 if facing == 'East' else 0
    face_n = 1 if facing == 'North' else 0
    face_s = 1 if facing == 'South' else 0
    face_w = 1 if facing == 'West' else 0

    # One-hot: Owner_Type
    own_br = 1 if owner_type == 'Broker' else 0
    own_bl = 1 if owner_type == 'Builder' else 0
    own_ow = 1 if owner_type == 'Owner' else 0

    row = {
        'BHK': bhk,
        'Size_in_SqFt': size_sqft,
        'Floor_No': floor_no,
        'Total_Floors': total_floors,
        'Age_of_Property': age,
        'Nearby_Schools': nearby_schools,
        'Nearby_Hospitals': nearby_hospitals,
        'Public_Transport_Accessibility': transport_enc,
        'Parking_Space': parking_enc,
        'Security': security_enc,
        'Availability_Status': availability_enc,
        'Bathrooms': bhk,
        'Balcony': balcony,
        'Population_Density': population_density,
        'Mall_Distance_km': mall_distance,
        'Crime_Index': crime_index,
        'Infra_Growth_Score': infra_growth_score,
        'Amenity_Count': amenity_count,
        'Floor_Ratio': floor_ratio,
        'State_Encoded': state_enc,
        'City_Encoded': city_enc,
        'Property_Type_Apartment': prop_apt,
        'Property_Type_Independent House': prop_ind,
        'Property_Type_Villa': prop_vil,
        'Furnished_Status_Furnished': furn_f,
        'Furnished_Status_Semi-furnished': furn_sf,
        'Furnished_Status_Unfurnished': furn_uf,
        'Facing_East': face_e,
        'Facing_North': face_n,
        'Facing_South': face_s,
        'Facing_West': face_w,
        'Owner_Type_Broker': own_br,
        'Owner_Type_Builder': own_bl,
        'Owner_Type_Owner': own_ow,
    }

    df_input = pd.DataFrame([row])[FEATURES]
    return df_input

def predict_price(input_df):
    """Returns predicted price in Lakhs."""
    prediction = model.predict(input_df)[0]
    return round(float(prediction), 2)