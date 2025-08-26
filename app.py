from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from datetime import datetime
import json

app = Flask(__name__)

# Global variables
llc_data = None

# Context processor to make states_data available in all templates
@app.context_processor
def inject_states_data():
    return dict(states_data=states_data)

# Context processor to make top cities available in all templates
@app.context_processor
def inject_top_cities():
    if llc_data is not None:
        # Get city counts
        city_counts = llc_data.groupby(['city', 'state']).size().reset_index(name='count')
        city_counts = city_counts.sort_values('count', ascending=False)
        
        # Get top 50 cities
        top_cities = []
        for _, row in city_counts.head(50).iterrows():
            state_abbr = row['state']
            state_slug = next((slug for slug, info in states_data.items() 
                              if info['abbr'].lower() == state_abbr.lower() or 
                                 info['name'].lower() == state_abbr.lower()), None)
            
            if state_slug:
                top_cities.append({
                    'city': row['city'],
                    'state': state_abbr,
                    'state_name': states_data[state_slug]['name'],
                    'state_slug': state_slug,
                    'city_slug': generate_seo_url(row['city']),
                    'count': row['count']
                })
        return dict(top_cities=top_cities)
    return dict(top_cities=[])
states_data = {
    'alabama': {'name': 'Alabama', 'abbr': 'AL', 'formation_fee': 200, 'annual_fee': 100},
    'alaska': {'name': 'Alaska', 'abbr': 'AK', 'formation_fee': 250, 'annual_fee': 100},
    'arizona': {'name': 'Arizona', 'abbr': 'AZ', 'formation_fee': 50, 'annual_fee': 0},
    'arkansas': {'name': 'Arkansas', 'abbr': 'AR', 'formation_fee': 45, 'annual_fee': 150},
    'california': {'name': 'California', 'abbr': 'CA', 'formation_fee': 70, 'annual_fee': 800},
    'colorado': {'name': 'Colorado', 'abbr': 'CO', 'formation_fee': 50, 'annual_fee': 10},
    'connecticut': {'name': 'Connecticut', 'abbr': 'CT', 'formation_fee': 120, 'annual_fee': 20},
    'delaware': {'name': 'Delaware', 'abbr': 'DE', 'formation_fee': 90, 'annual_fee': 300},
    'florida': {'name': 'Florida', 'abbr': 'FL', 'formation_fee': 125, 'annual_fee': 138.75},
    'georgia': {'name': 'Georgia', 'abbr': 'GA', 'formation_fee': 100, 'annual_fee': 50},
    'hawaii': {'name': 'Hawaii', 'abbr': 'HI', 'formation_fee': 50, 'annual_fee': 15},
    'idaho': {'name': 'Idaho', 'abbr': 'ID', 'formation_fee': 100, 'annual_fee': 0},
    'illinois': {'name': 'Illinois', 'abbr': 'IL', 'formation_fee': 150, 'annual_fee': 75},
    'indiana': {'name': 'Indiana', 'abbr': 'IN', 'formation_fee': 90, 'annual_fee': 30},
    'iowa': {'name': 'Iowa', 'abbr': 'IA', 'formation_fee': 50, 'annual_fee': 30},
    'kansas': {'name': 'Kansas', 'abbr': 'KS', 'formation_fee': 165, 'annual_fee': 55},
    'kentucky': {'name': 'Kentucky', 'abbr': 'KY', 'formation_fee': 40, 'annual_fee': 15},
    'louisiana': {'name': 'Louisiana', 'abbr': 'LA', 'formation_fee': 100, 'annual_fee': 35},
    'maine': {'name': 'Maine', 'abbr': 'ME', 'formation_fee': 175, 'annual_fee': 85},
    'maryland': {'name': 'Maryland', 'abbr': 'MD', 'formation_fee': 100, 'annual_fee': 300},
    'massachusetts': {'name': 'Massachusetts', 'abbr': 'MA', 'formation_fee': 500, 'annual_fee': 500},
    'michigan': {'name': 'Michigan', 'abbr': 'MI', 'formation_fee': 50, 'annual_fee': 25},
    'minnesota': {'name': 'Minnesota', 'abbr': 'MN', 'formation_fee': 155, 'annual_fee': 25},
    'mississippi': {'name': 'Mississippi', 'abbr': 'MS', 'formation_fee': 50, 'annual_fee': 25},
    'missouri': {'name': 'Missouri', 'abbr': 'MO', 'formation_fee': 50, 'annual_fee': 0},
    'montana': {'name': 'Montana', 'abbr': 'MT', 'formation_fee': 70, 'annual_fee': 20},
    'nebraska': {'name': 'Nebraska', 'abbr': 'NE', 'formation_fee': 100, 'annual_fee': 10},
    'nevada': {'name': 'Nevada', 'abbr': 'NV', 'formation_fee': 75, 'annual_fee': 325},
    'new-hampshire': {'name': 'New Hampshire', 'abbr': 'NH', 'formation_fee': 100, 'annual_fee': 100},
    'new-jersey': {'name': 'New Jersey', 'abbr': 'NJ', 'formation_fee': 125, 'annual_fee': 75},
    'new-mexico': {'name': 'New Mexico', 'abbr': 'NM', 'formation_fee': 50, 'annual_fee': 0},
    'new-york': {'name': 'New York', 'abbr': 'NY', 'formation_fee': 200, 'annual_fee': 9},
    'north-carolina': {'name': 'North Carolina', 'abbr': 'NC', 'formation_fee': 125, 'annual_fee': 200},
    'north-dakota': {'name': 'North Dakota', 'abbr': 'ND', 'formation_fee': 135, 'annual_fee': 50},
    'ohio': {'name': 'Ohio', 'abbr': 'OH', 'formation_fee': 99, 'annual_fee': 0},
    'oklahoma': {'name': 'Oklahoma', 'abbr': 'OK', 'formation_fee': 100, 'annual_fee': 25},
    'oregon': {'name': 'Oregon', 'abbr': 'OR', 'formation_fee': 100, 'annual_fee': 100},
    'pennsylvania': {'name': 'Pennsylvania', 'abbr': 'PA', 'formation_fee': 125, 'annual_fee': 70},
    'rhode-island': {'name': 'Rhode Island', 'abbr': 'RI', 'formation_fee': 150, 'annual_fee': 50},
    'south-carolina': {'name': 'South Carolina', 'abbr': 'SC', 'formation_fee': 110, 'annual_fee': 0},
    'south-dakota': {'name': 'South Dakota', 'abbr': 'SD', 'formation_fee': 150, 'annual_fee': 50},
    'tennessee': {'name': 'Tennessee', 'abbr': 'TN', 'formation_fee': 300, 'annual_fee': 300},
    'texas': {'name': 'Texas', 'abbr': 'TX', 'formation_fee': 300, 'annual_fee': 0},
    'utah': {'name': 'Utah', 'abbr': 'UT', 'formation_fee': 70, 'annual_fee': 20},
    'vermont': {'name': 'Vermont', 'abbr': 'VT', 'formation_fee': 125, 'annual_fee': 35},
    'virginia': {'name': 'Virginia', 'abbr': 'VA', 'formation_fee': 100, 'annual_fee': 50},
    'washington': {'name': 'Washington', 'abbr': 'WA', 'formation_fee': 200, 'annual_fee': 60},
    'west-virginia': {'name': 'West Virginia', 'abbr': 'WV', 'formation_fee': 100, 'annual_fee': 25},
    'wisconsin': {'name': 'Wisconsin', 'abbr': 'WI', 'formation_fee': 130, 'annual_fee': 25},
    'wyoming': {'name': 'Wyoming', 'abbr': 'WY', 'formation_fee': 100, 'annual_fee': 50}
}

def load_llc_data(csv_file='LLC Data.csv'):
    """Load LLC data from CSV file"""
    global llc_data
    try:
        # Try multiple possible paths for the CSV file
        possible_paths = [
            csv_file,  # Current directory
            os.path.join(os.path.dirname(__file__), csv_file),  # Same directory as app.py
            os.path.join(os.getcwd(), csv_file),  # Current working directory
            'C:\\llc-formation-website\\LLC Data.csv',  # Windows absolute path (fallback)
        ]
        
        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                print(f"Found CSV file at: {csv_path}")
                break
        
        if csv_path is None:
            print(f"CSV file not found. Tried paths: {possible_paths}")
            # Create some sample data for testing
            print("Creating sample data for testing...")
            sample_data = {
                'name': ['Sample LLC Service', 'Business Formation Co', 'Legal Services LLC'],
                'city': ['New York', 'Los Angeles', 'Chicago'],
                'state': ['NY', 'CA', 'IL'],
                'postal_code': ['10001', '90210', '60601']
            }
            llc_data = pd.DataFrame(sample_data)
            print(f"Created sample data with {len(llc_data)} records")
            return True
        
        # Load the actual CSV file
        llc_data = pd.read_csv(csv_path)
        print(f"Successfully loaded CSV from: {csv_path}")
        
            # Clean and process data
            llc_data = llc_data.fillna('')
        
        # Check if required columns exist
        required_columns = ['name', 'city', 'state']
        missing_columns = [col for col in required_columns if col not in llc_data.columns]
        if missing_columns:
            print(f"Warning: Missing required columns: {missing_columns}")
            print(f"Available columns: {list(llc_data.columns)}")
            # Create sample data if required columns are missing
            sample_data = {
                'name': ['Sample LLC Service', 'Business Formation Co', 'Legal Services LLC'],
                'city': ['New York', 'Los Angeles', 'Chicago'],
                'state': ['NY', 'CA', 'IL'],
                'postal_code': ['10001', '90210', '60601']
            }
            llc_data = pd.DataFrame(sample_data)
            print(f"Created sample data with {len(llc_data)} records")
            return True
        
            # Filter for business data (remove rows with empty business names)
            llc_data = llc_data[llc_data['name'].notna() & (llc_data['name'] != '')]
            print(f"Loaded {len(llc_data)} business records")
            
            # Debug: Show sample of city, postal_code, and state data
            print("Sample city/postal_code/state data:")
            if 'postal_code' in llc_data.columns:
                sample_data = llc_data[['name', 'city', 'postal_code', 'state']].head(10)
            else:
                sample_data = llc_data[['name', 'city', 'state']].head(10)
            print(sample_data)
            
            # Check for unique cities and states
            print(f"Unique cities: {llc_data['city'].nunique()}")
            print(f"Unique states: {llc_data['state'].nunique()}")
            if 'postal_code' in llc_data.columns:
                print(f"Unique postal codes: {llc_data['postal_code'].nunique()}")
            
            return True
        
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        print("Creating sample data due to error...")
        # Create sample data as fallback
        sample_data = {
            'name': ['Sample LLC Service', 'Business Formation Co', 'Legal Services LLC'],
            'city': ['New York', 'Los Angeles', 'Chicago'],
            'state': ['NY', 'CA', 'IL'],
            'postal_code': ['10001', '90210', '60601']
        }
        llc_data = pd.DataFrame(sample_data)
        print(f"Created sample data with {len(llc_data)} records")
        return True

def generate_seo_url(text):
    """Generate SEO-friendly URL from text"""
    if pd.isna(text) or text == '':
        return ''
    return text.lower().replace(' ', '-').replace(',', '').replace('.', '').replace("'", '').replace('"', '')

def get_structured_data(business_type="Service", name="Business Directory", description="Find local businesses"):
    """Generate structured data for SEO"""
    return {
        "@context": "https://schema.org",
        "@type": business_type,
        "name": name,
        "description": description,
        "provider": {
            "@type": "Organization",
            "name": "Business Directory"
        }
    }

@app.route('/')
def index():
    """Homepage - LLC Formation Services Directory"""
    title = "LLC Formation Services Directory - Find Local Business Formation Providers"
    meta_description = "Find local LLC formation services with reviews and contact information. Browse by city, state, or search for business formation providers near you."
    
    # Get cities by state for dropdown
    cities_by_state = {}
    if llc_data is not None and len(llc_data) > 0:
        print(f"Processing {len(llc_data)} rows for cities by state")
        # Group cities by state
        for _, row in llc_data.iterrows():
            state = row['state']
            city = row['city']
            if state and city:
                if state not in cities_by_state:
                    cities_by_state[state] = set()
                cities_by_state[state].add(city)
        
        # Convert sets to sorted lists
        for state in cities_by_state:
            cities_by_state[state] = sorted(list(cities_by_state[state]))
        
        print(f"Created cities_by_state with {len(cities_by_state)} states")
        if cities_by_state:
            sample_state = list(cities_by_state.keys())[0]
            print(f"Sample state {sample_state}: {len(cities_by_state[sample_state])} cities")
    
    # Get popular cities (top 50)
    popular_cities = []
    if llc_data is not None and len(llc_data) > 0:
        city_counts = llc_data['city'].value_counts().head(50)
        
        for city, count in city_counts.items():
            # Get the state for this city (take the first occurrence)
            city_data = llc_data[llc_data['city'] == city].iloc[0]
            state = city_data['state']
            
            # Find the state slug
            state_slug = None
            for slug, info in states_data.items():
                if info['abbr'].lower() == state.lower() or info['name'].lower() == state.lower():
                    state_slug = slug
                    break
            
            if state_slug:
                popular_cities.append({
                    'city': city,
                    'count': count,
                    'state': state,
                    'state_slug': state_slug,
                    'city_slug': generate_seo_url(city)
                })
    
    return render_template('index.html',
                         title=title,
                         meta_description=meta_description,
                         cities_by_state=cities_by_state,
                         popular_cities=popular_cities,
                         structured_data=get_structured_data("WebSite", "LLC Formation Services Directory", "Find local LLC formation services in your area"))



@app.route('/city/<state_slug>/<city_slug>')
@app.route('/city/<state_slug>/<city_slug>/page/<int:page>')
def city_directory(state_slug, city_slug, page=1):
    """City-specific business directory page with pagination"""
    if state_slug not in states_data:
        return "State not found", 404
    
    state_info = states_data[state_slug]
    per_page = 5  # Show 5 businesses per page
    
    # Get businesses in this city
    city_businesses = []
    state_businesses = []
    if llc_data is not None:
        # First filter by state - try multiple state field matches
        state_filtered = llc_data[
            (llc_data['state'].str.lower() == state_info['abbr'].lower()) |
            (llc_data['state'].str.lower() == state_info['name'].lower())
        ]
        
        # If no results, try us_state field if it exists
        if len(state_filtered) == 0 and 'us_state' in llc_data.columns:
            state_filtered = llc_data[
                (llc_data['us_state'].str.lower() == state_info['abbr'].lower()) |
                (llc_data['us_state'].str.lower() == state_info['name'].lower())
            ]
        
        # Store all state businesses for other cities section
        state_businesses = state_filtered.to_dict('records')
        
        # Then filter by city - try multiple matching strategies
        city_name_from_slug = city_slug.replace('-', ' ').title()
        
        # Try exact city name match (case insensitive)
        city_businesses = state_filtered[
            state_filtered['city'].str.lower() == city_name_from_slug.lower()
        ]
        
        # If no results, try slug-based matching
        if len(city_businesses) == 0:
            city_businesses = state_filtered[
                state_filtered['city'].str.lower().str.replace(' ', '-') == city_slug.lower()
            ]
        
        # If still no results, try partial matching
        if len(city_businesses) == 0:
            city_businesses = state_filtered[
                state_filtered['city'].str.lower().str.contains(city_name_from_slug.lower(), na=False)
            ]
        
        # If still no results, try matching the first word of the city name
        if len(city_businesses) == 0:
            first_word = city_name_from_slug.split()[0].lower()
            city_businesses = state_filtered[
                state_filtered['city'].str.lower().str.startswith(first_word, na=False)
            ]
        
        # If still no results, try case-insensitive contains
        if len(city_businesses) == 0:
            city_businesses = state_filtered[
                state_filtered['city'].str.lower().str.contains(city_slug.lower(), na=False)
            ]
        
        city_businesses = city_businesses.to_dict('records')
        
        # Debug output
        print(f"State: {state_info['abbr']}, City slug: {city_slug}")
        print(f"Total businesses in state: {len(state_filtered)}")
        print(f"Businesses found in city: {len(city_businesses)}")
        if len(city_businesses) > 0:
            print(f"Sample city names: {[b['city'] for b in city_businesses[:3]]}")
        else:
            print(f"Available cities in {state_info['abbr']}: {state_filtered['city'].unique()[:10]}")
    
    # Get city name from first business or use slug
    if len(city_businesses) > 0:
        city_name = city_businesses[0]['city']
    else:
        city_name = city_slug.replace('-', ' ').title()
    
    # Calculate rating statistics
    businesses_4_plus = 0
    businesses_3_plus = 0
    businesses_with_reviews = 0
    
    for business in city_businesses:
        # Check if business has a rating
        rating = business.get('rating', 0)
        if rating and rating > 0:
            businesses_with_reviews += 1
            if rating >= 4.0:
                businesses_4_plus += 1
            if rating >= 3.0:
                businesses_3_plus += 1
    
    # Calculate pagination
    total_businesses = len(city_businesses)
    total_pages = (total_businesses + per_page - 1) // per_page
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Get businesses for current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_businesses = city_businesses[start_idx:end_idx]
    
    title = f"Best LLC Formation Services in {city_name}, {state_info['abbr']} (2025 Reviews)"
    meta_description = f"Find the top-rated LLC formation services in {city_name}. Get professional help with business registration, legal services, and everything you need to start your LLC in {city_name}."
    
    return render_template('city_directory.html',
                         state=state_info,
                         city_name=city_name,
                         city_slug=city_slug,
                         businesses=current_page_businesses,
                         all_businesses=city_businesses,
                         state_businesses=state_businesses,
                         current_page=page,
                         total_pages=total_pages,
                         total_businesses=total_businesses,
                         per_page=per_page,
                         businesses_4_plus=businesses_4_plus,
                         businesses_3_plus=businesses_3_plus,
                         businesses_with_reviews=businesses_with_reviews,
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_city_structured_data(state_info, city_name))

def get_city_structured_data(state_info, city_name):
    """Generate structured data for city pages"""
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"Business Directory - {city_name}, {state_info['name']}",
        "description": f"Find local businesses in {city_name}, {state_info['name']}",
        "mainEntity": {
            "@type": "City",
            "name": city_name,
            "addressRegion": state_info['name'],
            "addressCountry": "US"
        }
    }

@app.route('/state/<state_slug>')
def state_directory(state_slug):
    """State-specific LLC formation services directory page"""
    if state_slug not in states_data:
        return "State not found", 404
    
    state_info = states_data[state_slug]
    
    # Debug: Print state info
    print(f"Debug: Looking for state {state_info['name']} ({state_info['abbr']})")
    
    # Get businesses in this state
    state_businesses = []
    total_businesses = 0
    if llc_data is not None:
        # Debug: Check available state columns
        print(f"Debug: Available columns: {list(llc_data.columns)}")
        print(f"Debug: Sample state values: {llc_data['state'].head(10).tolist()}")
        print(f"Debug: Sample us_state values: {llc_data['us_state'].head(10).tolist()}")
        
        # Try multiple state matching strategies
        state_businesses = llc_data[
            (llc_data['state'].str.lower() == state_info['abbr'].lower()) |
            (llc_data['us_state'].str.lower() == state_info['abbr'].lower()) |
            (llc_data['state'].str.lower() == state_info['name'].lower()) |
            (llc_data['us_state'].str.lower() == state_info['name'].lower())
        ]
        
        print(f"Debug: Found {len(state_businesses)} businesses for {state_info['name']}")
        total_businesses = len(state_businesses)
        state_businesses = state_businesses.to_dict('records')
    
    # Get cities in this state
    cities = []
    if llc_data is not None:
        state_data = llc_data[
            (llc_data['state'].str.lower() == state_info['abbr'].lower()) |
            (llc_data['us_state'].str.lower() == state_info['abbr'].lower()) |
            (llc_data['state'].str.lower() == state_info['name'].lower()) |
            (llc_data['us_state'].str.lower() == state_info['name'].lower())
        ]
        
        print(f"Debug: Cities found: {state_data['city'].value_counts().head(10).to_dict()}")
        city_counts = state_data['city'].value_counts()
        cities = [{'city': city, 'count': count, 'slug': generate_seo_url(city)} 
                 for city, count in city_counts.items()]
    
    title = f"LLC Formation Services in {state_info['name']} (2025 Directory)"
    meta_description = f"Find the best LLC formation services in {state_info['name']}. Get professional help with business registration, legal services, and everything you need to start your LLC in {state_info['name']}."
    
    return render_template('state_directory.html',
                         state=state_info,
                         businesses=state_businesses,
                         cities=cities,
                         total_businesses=total_businesses,
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_state_structured_data(state_info))

def get_state_structured_data(state_info):
    """Generate structured data for state pages"""
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": f"Business Directory - {state_info['name']}",
        "description": f"Find local businesses in {state_info['name']}",
        "mainEntity": {
            "@type": "State",
            "name": state_info['name'],
            "addressCountry": "US"
        }
    }



@app.route('/category/<category_slug>')
def category_directory(category_slug):
    """Category-specific business directory"""
    category_name = category_slug.replace('-', ' ').title()
    
    category_businesses = []
    if llc_data is not None:
        category_businesses = llc_data[
            llc_data['category'].str.contains(category_name, case=False, na=False)
        ]
        category_businesses = category_businesses.to_dict('records')
    
    title = f"{category_name} Businesses - Business Directory"
    meta_description = f"Find {category_name} businesses near you. Browse with reviews and contact information."
    
    return render_template('category_directory.html',
                         title=title,
                         meta_description=meta_description,
                         category_name=category_name,
                         category_slug=category_slug,
                         businesses=category_businesses,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/about')
def about():
    """About page"""
    title = "About Our Business Directory"
    meta_description = "Learn about our comprehensive business directory. Find local businesses, read reviews, and connect with services in your area."
    
    return render_template('about.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/privacy-policy')
def privacy_policy():
    """Privacy Policy page"""
    title = "Privacy Policy - Rigma Marketing LLC"
    meta_description = "Privacy Policy for Rigma Marketing LLC. Learn how we collect, use, and protect your information, including affiliate tracking disclosure."
    
    return render_template('privacy_policy.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/terms-conditions')
def terms_conditions():
    """Terms and Conditions page"""
    title = "Terms and Conditions - Rigma Marketing LLC"
    meta_description = "Terms and Conditions for Rigma Marketing LLC. Read our terms of service, user agreements, and legal policies for using our website."
    
    return render_template('terms_conditions.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/contact')
def contact():
    """Contact page"""
    title = "Contact Us - Business Directory"
    meta_description = "Contact our business directory team. Get help finding local businesses or list your business in our directory."
    
    return render_template('contact.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap"""
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Add static pages with high priority
    static_pages = [
        {'url': '', 'priority': '1.0', 'changefreq': 'daily'},
        {'url': '/about', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/contact', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/privacy-policy', 'priority': '0.6', 'changefreq': 'yearly'},
        {'url': '/terms-conditions', 'priority': '0.6', 'changefreq': 'yearly'}
    ]
    
    for page in static_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page["url"]}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>{page["changefreq"]}</changefreq>\n    <priority>{page["priority"]}</priority>\n  </url>\n'
    
    # Add directory pages
    directory_pages = [
        {'url': '/cities', 'priority': '0.9', 'changefreq': 'weekly'},
        {'url': '/all-locations', 'priority': '0.9', 'changefreq': 'weekly'}
    ]
    
    for page in directory_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page["url"]}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>{page["changefreq"]}</changefreq>\n    <priority>{page["priority"]}</priority>\n  </url>\n'
    
    # Add calculator pages
    calculator_pages = [
        {'url': '/calculators', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/calculator/break-even', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/calculator/roi', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/calculator/equity-split', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/calculator/business-loan', 'priority': '0.7', 'changefreq': 'monthly'}
    ]
    
    for page in calculator_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page["url"]}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>{page["changefreq"]}</changefreq>\n    <priority>{page["priority"]}</priority>\n  </url>\n'
    
    # Add resource pages
    resource_pages = [
        {'url': '/resources', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/business-structure-quiz', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/llc-cost-calculator', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/foreign-qualification-checklist', 'priority': '0.7', 'changefreq': 'monthly'}
    ]
    
    for page in resource_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page["url"]}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>{page["changefreq"]}</changefreq>\n    <priority>{page["priority"]}</priority>\n  </url>\n'
    
    # Add LLC guide pages
    guide_pages = [
        {'url': '/llc-formation-guide', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/llc-operating-agreement-guide', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/llc-tax-guide', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/llc-compliance-guide', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/llc-business-bank-account-guide', 'priority': '0.7', 'changefreq': 'monthly'}
    ]
    
    for page in guide_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page["url"]}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>{page["changefreq"]}</changefreq>\n    <priority>{page["priority"]}</priority>\n  </url>\n'
    
    # Add state pages
    for state_slug in states_data.keys():
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}/state/{state_slug}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    
    # Add city pages if we have LLC data
    if llc_data is not None:
        # Get unique city-state combinations
        city_states = llc_data[['city', 'state', 'us_state']].dropna().drop_duplicates()
        for _, row in city_states.iterrows():
            city = row['city']
            state_abbr = row['state'] if pd.notna(row['state']) else row['us_state']
            
            # Find matching state slug
            state_slug = None
            for slug, state_info in states_data.items():
                if state_info['abbr'].lower() == state_abbr.lower():
                    state_slug = slug
                    break
            
            if state_slug and city:
                city_slug = generate_seo_url(city)
                sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}/city/{state_slug}/{city_slug}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
    
    # Add category pages (if any)
    category_pages = [
        {'url': '/category/llc-formation-services', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/category/business-services', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/category/legal-services', 'priority': '0.7', 'changefreq': 'monthly'}
    ]
    
    for page in category_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page["url"]}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>{page["changefreq"]}</changefreq>\n    <priority>{page["priority"]}</priority>\n  </url>\n'
    

    
    sitemap += '</urlset>'
    
    response = app.response_class(sitemap, mimetype='application/xml')
    return response

@app.route('/cities')
def cities_directory():
    """Top cities with LLC formation services"""
    if llc_data is None:
        return "No data loaded", 500
    
    # Get city counts
    city_counts = llc_data.groupby(['city', 'state']).size().reset_index(name='count')
    city_counts = city_counts.sort_values('count', ascending=False)
    
    # Get top 50 cities
    top_cities = []
    for _, row in city_counts.head(50).iterrows():
        state_abbr = row['state']
        state_slug = next((slug for slug, info in states_data.items() 
                          if info['abbr'].lower() == state_abbr.lower() or 
                             info['name'].lower() == state_abbr.lower()), None)
        
        if state_slug:
            top_cities.append({
                'city': row['city'],
                'state': state_abbr,
                'state_name': states_data[state_slug]['name'],
                'state_slug': state_slug,
                'city_slug': generate_seo_url(row['city']),
                'count': row['count']
            })
    
    title = "Top Cities for LLC Formation Services (2025 Directory)"
    meta_description = "Find the best cities for LLC formation services. Browse our directory of top cities with the most LLC formation providers and business services."
    
    return render_template('cities_directory.html',
                         cities=top_cities,
                         title=title,
                         meta_description=meta_description)

@app.route('/all-locations')
def all_locations():
    """Complete directory of all cities and states with LLC formation services"""
    if llc_data is None:
        return "No data loaded", 500
    
    # Get all unique cities with counts
    city_counts = llc_data.groupby(['city', 'state']).size().reset_index(name='count')
    city_counts = city_counts.sort_values(['state', 'city'])
    
    # Get all unique states with counts
    state_counts = llc_data.groupby('state').size().reset_index(name='count')
    state_counts = state_counts.sort_values('state')
    
    # Process cities data
    all_cities = []
    for _, row in city_counts.iterrows():
        state_abbr = row['state']
        state_slug = next((slug for slug, info in states_data.items() 
                          if info['abbr'].lower() == state_abbr.lower() or 
                             info['name'].lower() == state_abbr.lower()), None)
        
        if state_slug:
            all_cities.append({
                'city': row['city'],
                'state': state_abbr,
                'state_name': states_data[state_slug]['name'],
                'state_slug': state_slug,
                'city_slug': generate_seo_url(row['city']),
                'count': row['count']
            })
    
    # Process states data
    all_states = []
    for _, row in state_counts.iterrows():
        state_abbr = row['state']
        state_slug = next((slug for slug, info in states_data.items() 
                          if info['abbr'].lower() == state_abbr.lower() or 
                             info['name'].lower() == state_abbr.lower()), None)
        
        if state_slug:
            all_states.append({
                'state': state_abbr,
                'state_name': states_data[state_slug]['name'],
                'state_slug': state_slug,
                'count': row['count']
            })
    
    title = "All Cities & States - Complete LLC Formation Services Directory"
    meta_description = "Browse our complete directory of all cities and states with LLC formation services. Find local business formation providers in every location across the United States."
    
    return render_template('all_locations.html',
                         cities=all_cities,
                         states=all_states,
                         title=title,
                         meta_description=meta_description)

@app.route('/debug/cities')
def debug_cities():
    """Debug route to see available cities"""
    if llc_data is None:
        return "No data loaded"
    
    # Get unique cities with their states and postal codes
    if 'postal_code' in llc_data.columns:
        cities_data = llc_data[['city', 'state', 'postal_code']].dropna().drop_duplicates()
    else:
        cities_data = llc_data[['city', 'state']].dropna().drop_duplicates()
    cities_data = cities_data.sort_values(['state', 'city'])
    
    # Convert to list for display
    cities_list = []
    for _, row in cities_data.iterrows():
        state_abbr = row['state']
        cities_list.append({
            'city': row['city'],
            'state': state_abbr,
            'postal_code': row.get('postal_code', ''),
            'city_slug': generate_seo_url(row['city']),
            'state_slug': next((slug for slug, info in states_data.items() if info['abbr'].lower() == state_abbr.lower() or info['name'].lower() == state_abbr.lower()), None)
        })
    
    return jsonify({
        'total_cities': len(cities_list),
        'cities': cities_list[:50]  # Show first 50
    })

@app.route('/debug/states')
def debug_states():
    """Debug route to show states in the data"""
    if llc_data is None:
        return "No data loaded", 500
    
    # Get state counts
    state_counts = llc_data['state'].value_counts()
    us_state_counts = llc_data['us_state'].value_counts()
    
    return jsonify({
        'state_counts': state_counts.head(20).to_dict(),
        'us_state_counts': us_state_counts.head(20).to_dict(),
        'total_records': len(llc_data),
        'sample_states': llc_data['state'].head(10).tolist(),
        'sample_us_states': llc_data['us_state'].head(10).tolist()
    })

@app.route('/robots.txt')
def robots():
    """Generate robots.txt"""
    robots_txt = "User-agent: *\n"
    robots_txt += "Allow: /\n"
    robots_txt += f"Sitemap: {request.host_url.rstrip('/')}/sitemap.xml\n"
    return app.response_class(robots_txt, mimetype='text/plain')

@app.route('/calculators')
def calculators():
    """Calculators landing page"""
    title = "Business Calculators - LLC Formation Tools"
    meta_description = "Free business calculators for LLC formation. Calculate break-even analysis, ROI, and equity splits for your business."
    
    return render_template('calculators.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/calculator/break-even')
def break_even_calculator():
    """Break-even calculator"""
    title = "Break-Even Calculator - Free Business Tool"
    meta_description = "Calculate your business break-even point. Free online tool to determine when your LLC will start making a profit."
    
    return render_template('break_even_calculator.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/calculator/roi')
def roi_calculator():
    """ROI calculator"""
    title = "ROI Calculator - Return on Investment Tool"
    meta_description = "Calculate your return on investment (ROI). Free online tool to analyze the profitability of your business investments."
    
    return render_template('roi_calculator.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/calculator/equity-split')
def equity_split_calculator():
    """Equity split calculator for multi-member LLCs"""
    title = "Equity Split Calculator - Multi-Member LLC Tool"
    meta_description = "Calculate equity splits for multi-member LLCs. Free online tool to determine fair ownership percentages."
    
    return render_template('equity_split_calculator.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/calculator/business-loan')
def business_loan_calculator():
    """Business loan calculator"""
    title = "Business Loan Calculator - Free Loan Payment Tool"
    meta_description = "Calculate business loan payments, interest, and amortization. Free online tool to determine loan costs and payment schedules."
    
    return render_template('business_loan_calculator.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/resources')
def resources():
    """Resources landing page"""
    title = "Business Resources - LLC Formation Tools & Guides"
    meta_description = "Comprehensive business resources for LLC formation. Access calculators, quizzes, checklists, and expert guidance to start your business."
    
    return render_template('resources.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/business-structure-quiz')
def business_structure_quiz():
    """Business structure quiz"""
    title = "Business Structure Quiz - Find Your Perfect Business Type"
    meta_description = "Take our business structure quiz to determine if an LLC, S-Corp, or C-Corp is right for your business goals and circumstances."
    
    return render_template('business_structure_quiz.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/llc-cost-calculator')
def llc_cost_calculator():
    """LLC formation cost calculator"""
    title = "LLC Formation Cost Calculator - State-by-State Pricing"
    meta_description = "Calculate the total cost of forming an LLC in your state. Compare service providers and get accurate pricing for your business formation."
    
    return render_template('llc_cost_calculator.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/foreign-qualification-checklist')
def foreign_qualification_checklist():
    """Foreign qualification checklist"""
    title = "Foreign Qualification Checklist - Multi-State Business Guide"
    meta_description = "Interactive checklist to determine if you need foreign qualification and track your compliance requirements for multi-state business operations."
    
    return render_template('foreign_qualification_checklist.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

# LLC Guides Routes
@app.route('/llc-formation-guide')
def llc_formation_guide():
    """LLC formation guide"""
    title = "LLC Formation Guide - Step-by-Step Business Formation"
    meta_description = "Complete guide to forming an LLC. Learn the step-by-step process, requirements, and best practices for starting your limited liability company."
    
    return render_template('llc_formation_guide.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/llc-operating-agreement-guide')
def llc_operating_agreement_guide():
    """LLC operating agreement guide"""
    title = "LLC Operating Agreement Guide - Essential Business Document"
    meta_description = "Complete guide to LLC operating agreements. Learn what to include, how to create one, and why it's essential for your business."
    
    return render_template('llc_operating_agreement_guide.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/llc-tax-guide')
def llc_tax_guide():
    """LLC tax guide"""
    title = "LLC Tax Guide - Understanding Business Taxation"
    meta_description = "Complete guide to LLC taxation. Learn about pass-through taxation, self-employment taxes, and tax filing requirements for your business."
    
    return render_template('llc_tax_guide.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/llc-compliance-guide')
def llc_compliance_guide():
    """LLC compliance guide"""
    title = "LLC Compliance Guide - Maintaining Your Business Legally"
    meta_description = "Complete guide to LLC compliance requirements. Learn about annual reports, state filings, and maintaining your business in good standing."
    
    return render_template('llc_compliance_guide.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

@app.route('/llc-business-bank-account-guide')
def llc_business_bank_account_guide():
    """LLC business bank account guide"""
    title = "LLC Business Bank Account Guide - Setting Up Business Banking"
    meta_description = "Complete guide to opening a business bank account for your LLC. Learn requirements, documentation, and best practices for business banking."
    
    return render_template('llc_business_bank_account_guide.html',
                         title=title,
                         meta_description=meta_description,
                         structured_data=get_structured_data("WebPage", title, meta_description))

    # Load data on startup
    load_llc_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
