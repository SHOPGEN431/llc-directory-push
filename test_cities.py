import pandas as pd

# Load the CSV data
df = pd.read_csv('C:\\llc-formation-website\\LLC Data.csv')

print("=== CSV Data Analysis ===")
print(f"Total records: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Check for city, postal_code, and state columns
if 'city' in df.columns:
    print(f"\nUnique cities: {df['city'].nunique()}")
    print("Sample cities:")
    print(df['city'].dropna().unique()[:20])

if 'state' in df.columns:
    print(f"\nUnique states: {df['state'].nunique()}")
    print("Sample states:")
    print(df['state'].dropna().unique()[:20])

if 'postal_code' in df.columns:
    print(f"\nUnique postal codes: {df['postal_code'].nunique()}")

# Check for Nevada/Las Vegas specifically
print("\n=== Nevada/Las Vegas Check ===")
nevada_data = df[df['state'].str.contains('Nevada|NV', case=False, na=False)]
print(f"Records in Nevada: {len(nevada_data)}")

if len(nevada_data) > 0:
    print("Cities in Nevada:")
    nevada_cities = nevada_data['city'].dropna().unique()
    print(nevada_cities)
    
    # Check for Las Vegas specifically
    vegas_data = nevada_data[nevada_data['city'].str.contains('Las Vegas|Vegas', case=False, na=False)]
    print(f"\nLas Vegas records: {len(vegas_data)}")
    if len(vegas_data) > 0:
        print("Las Vegas city names found:")
        print(vegas_data['city'].unique())

# Check for any city containing "vegas"
vegas_anywhere = df[df['city'].str.contains('vegas', case=False, na=False)]
print(f"\nAny city with 'vegas': {len(vegas_anywhere)}")
if len(vegas_anywhere) > 0:
    print("Cities with 'vegas':")
    print(vegas_anywhere[['city', 'state']].drop_duplicates())





