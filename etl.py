import pandas as pd
import numpy as np

print("Starting Supply Chain ETL script...")

# --- 1. LOAD DATA ---
try:
    df = pd.read_csv('supply_data.csv')
except FileNotFoundError:
    print("Error: 'supply_data.csv' not found.")
    print("Please download the dataset from Kaggle and rename it.")
    exit()

# --- 2. CLEAN DATA & RENAME COLUMNS ---
print("Cleaning data and renaming columns...")

# We are only keeping the columns we need for the dashboard
df_clean = df[['Scheduled Delivery Date', 'Delivered to Client Date', 
               'Shipment Mode', 'Freight Cost (USD)', 'Country']].copy()

# Rename columns to our standard format
df_clean = df_clean.rename(columns={
    'Scheduled Delivery Date': 'estimated_delivery_date',
    'Delivered to Client Date': 'actual_delivery_date',
    'Shipment Mode': 'carrier_name', # Using 'Shipment Mode' as the carrier
    'Freight Cost (USD)': 'shipping_cost',
    'Country': 'destination_country'
})

# --- 3. FIX DATA TYPES ---

# A) Clean the shipping_cost column
# This column has text like 'Freight Included in Commodity Cost'
# We'll convert those to 'NaN' (Not a Number) so we can treat it as numeric
df_clean['shipping_cost'] = pd.to_numeric(df_clean['shipping_cost'], errors='coerce')

# B) Convert date columns
df_clean['actual_delivery_date'] = pd.to_datetime(df_clean['actual_delivery_date'])
df_clean['estimated_delivery_date'] = pd.to_datetime(df_clean['estimated_delivery_date'])

# C) Drop any rows that are now empty after our cleaning
df_clean = df_clean.dropna(subset=[
    'actual_delivery_date', 
    'estimated_delivery_date', 
    'shipping_cost', 
    'carrier_name', 
    'destination_country'
])

# --- 4. FEATURE ENGINEERING (Creating KPIs) ---
print("Engineering features (KPIs)...")

# KPI 1: Delivery Time (in days)
df_clean['delivery_time_days'] = (df_clean['actual_delivery_date'] - df_clean['estimated_delivery_date']).dt.days

# KPI 2: On-Time Status (1 for on-time, 0 for late)
df_clean['on_time'] = np.where(df_clean['delivery_time_days'] <= 0, 1, 0)

# KPI 3: Shipping Route (Renamed, since we only have destination)
# This is our "route" for this project
df_clean['route'] = df_clean['destination_country']

# --- 5. EXPORT CLEANED DATA ---
output_path = 'analytics_data.csv'
df_clean.to_csv(output_path, index=False)

print(f"\nSuccess! Clean data saved to {output_path}")
print(df_clean.head())
