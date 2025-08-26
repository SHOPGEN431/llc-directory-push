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
    # For Vercel deployment, use sample data
    sample_cities = [
        {'city': 'New York', 'state': 'NY', 'state_name': 'New York', 'state_slug': 'new-york', 'count': 150},
        {'city': 'Los Angeles', 'state': 'CA', 'state_name': 'California', 'state_slug': 'california', 'count': 120},
        {'city': 'Chicago', 'state': 'IL', 'state_name': 'Illinois', 'state_slug': 'illinois', 'count': 100},
        {'city': 'Houston', 'state': 'TX', 'state_name': 'Texas', 'state_slug': 'texas', 'count': 90},
        {'city': 'Phoenix', 'state': 'AZ', 'state_name': 'Arizona', 'state_slug': 'arizona', 'count': 80}
    ]
    
    top_cities = []
    for city_info in sample_cities:
        top_cities.append({
            'city': city_info['city'],
            'state': city_info['state'],
            'state_name': city_info['state_name'],
            'state_slug': city_info['state_slug'],
            'city_slug': generate_seo_url(city_info['city']),
            'count': city_info['count']
        })
    
    return dict(top_cities=top_cities)
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

def load_llc_data(csv_file=None):
    """Load LLC data from CSV file"""
    global llc_data
    try:
        # For Vercel deployment, we'll work without CSV data for now
        # You can add the CSV file later or use a database
        print("Running without CSV data for Vercel deployment")
        llc_data = None
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

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
    
    # For Vercel deployment, we'll use static data
    cities_by_state = {}
    popular_cities = []
    
    # Create some sample popular cities for demonstration
    sample_cities = [
        {'city': 'New York', 'state': 'NY', 'state_slug': 'new-york', 'count': 150},
        {'city': 'Los Angeles', 'state': 'CA', 'state_slug': 'california', 'count': 120},
        {'city': 'Chicago', 'state': 'IL', 'state_slug': 'illinois', 'count': 100},
        {'city': 'Houston', 'state': 'TX', 'state_slug': 'texas', 'count': 90},
        {'city': 'Phoenix', 'state': 'AZ', 'state_slug': 'arizona', 'count': 80},
        {'city': 'Philadelphia', 'state': 'PA', 'state_slug': 'pennsylvania', 'count': 75},
        {'city': 'San Antonio', 'state': 'TX', 'state_slug': 'texas', 'count': 70},
        {'city': 'San Diego', 'state': 'CA', 'state_slug': 'california', 'count': 65},
        {'city': 'Dallas', 'state': 'TX', 'state_slug': 'texas', 'count': 60},
        {'city': 'San Jose', 'state': 'CA', 'state_slug': 'california', 'count': 55}
    ]
    
    for city_info in sample_cities:
        popular_cities.append({
            'city': city_info['city'],
            'count': city_info['count'],
            'state': city_info['state'],
            'state_slug': city_info['state_slug'],
            'city_slug': generate_seo_url(city_info['city'])
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
    
    # For Vercel deployment, use sample data
    city_name = city_slug.replace('-', ' ').title()
    
    # Sample businesses for demonstration
    sample_businesses = [
        {
            'name': 'Northwest Registered Agent',
            'rating': 4.8,
            'reviews': 1250,
            'address': f'123 Business Ave, {city_name}, {state_info["abbr"]}',
            'phone': '(555) 123-4567',
            'website': 'https://consumer-champion.org/LLCwebsite',
            'description': 'Professional LLC formation services with registered agent support.',
            'services': ['LLC Formation', 'Registered Agent', 'Compliance'],
            'price': '$39 + State Fees'
        },
        {
            'name': 'FileNow',
            'rating': 4.5,
            'reviews': 890,
            'address': f'456 Corporate Blvd, {city_name}, {state_info["abbr"]}',
            'phone': '(555) 234-5678',
            'website': 'https://filenow.com',
            'description': 'Fast and affordable business formation services.',
            'services': ['LLC Formation', 'EIN', 'Operating Agreement'],
            'price': '$49 + State Fees'
        },
        {
            'name': 'Bizee',
            'rating': 4.3,
            'reviews': 650,
            'address': f'789 Startup St, {city_name}, {state_info["abbr"]}',
            'phone': '(555) 345-6789',
            'website': 'https://bizee.com',
            'description': 'Comprehensive business formation and compliance services.',
            'services': ['LLC Formation', 'Compliance', 'Business Tools'],
            'price': '$59 + State Fees'
        }
    ]
    
    city_businesses = sample_businesses
    state_businesses = sample_businesses
    
    # Calculate rating statistics
    businesses_4_plus = len([b for b in city_businesses if b.get('rating', 0) >= 4.0])
    businesses_3_plus = len([b for b in city_businesses if b.get('rating', 0) >= 3.0])
    businesses_with_reviews = len([b for b in city_businesses if b.get('rating', 0) > 0])
    
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
    
    # For Vercel deployment, use sample data
    sample_businesses = [
        {
            'name': 'Northwest Registered Agent',
            'rating': 4.8,
            'reviews': 1250,
            'address': f'123 Business Ave, {state_info["name"]}',
            'phone': '(555) 123-4567',
            'website': 'https://consumer-champion.org/LLCwebsite',
            'description': 'Professional LLC formation services with registered agent support.',
            'services': ['LLC Formation', 'Registered Agent', 'Compliance'],
            'price': '$39 + State Fees'
        },
        {
            'name': 'FileNow',
            'rating': 4.5,
            'reviews': 890,
            'address': f'456 Corporate Blvd, {state_info["name"]}',
            'phone': '(555) 234-5678',
            'website': 'https://filenow.com',
            'description': 'Fast and affordable business formation services.',
            'services': ['LLC Formation', 'EIN', 'Operating Agreement'],
            'price': '$49 + State Fees'
        },
        {
            'name': 'Bizee',
            'rating': 4.3,
            'reviews': 650,
            'address': f'789 Startup St, {state_info["name"]}',
            'phone': '(555) 345-6789',
            'website': 'https://bizee.com',
            'description': 'Comprehensive business formation and compliance services.',
            'services': ['LLC Formation', 'Compliance', 'Business Tools'],
            'price': '$59 + State Fees'
        }
    ]
    
    state_businesses = sample_businesses
    total_businesses = len(state_businesses)
    
    # Sample cities for the state
    sample_cities = [
        {'city': 'Capital City', 'count': 45, 'slug': 'capital-city'},
        {'city': 'Metro City', 'count': 38, 'slug': 'metro-city'},
        {'city': 'Business Town', 'count': 32, 'slug': 'business-town'},
        {'city': 'Commerce City', 'count': 28, 'slug': 'commerce-city'},
        {'city': 'Enterprise Town', 'count': 25, 'slug': 'enterprise-town'}
    ]
    
    cities = sample_cities
    
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
    
    # Add static pages
    static_pages = ['', '/about', '/contact', '/privacy-policy', '/terms-conditions']
    for page in static_pages:
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}{page}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
    
    # Add state pages
    for state_slug in states_data.keys():
        sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}/state/{state_slug}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
    
    # Add sample city pages for Vercel deployment
    sample_cities = [
        {'city': 'New York', 'state': 'NY'},
        {'city': 'Los Angeles', 'state': 'CA'},
        {'city': 'Chicago', 'state': 'IL'},
        {'city': 'Houston', 'state': 'TX'},
        {'city': 'Phoenix', 'state': 'AZ'}
    ]
    
    for city_info in sample_cities:
        city = city_info['city']
        state_abbr = city_info['state']
        
        # Find matching state slug
        state_slug = None
        for slug, state_info in states_data.items():
            if state_info['abbr'].lower() == state_abbr.lower():
                state_slug = slug
                break
        
        if state_slug and city:
            city_slug = generate_seo_url(city)
            sitemap += f'  <url>\n    <loc>{request.host_url.rstrip("/")}/city/{state_slug}/{city_slug}</loc>\n    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
    
    sitemap += '</urlset>'
    
    response = app.response_class(sitemap, mimetype='application/xml')
    return response

@app.route('/cities')
def cities_directory():
    """Top cities with LLC formation services"""
    # For Vercel deployment, use sample data
    sample_cities = [
        {'city': 'New York', 'state': 'NY', 'state_name': 'New York', 'state_slug': 'new-york', 'count': 150},
        {'city': 'Los Angeles', 'state': 'CA', 'state_name': 'California', 'state_slug': 'california', 'count': 120},
        {'city': 'Chicago', 'state': 'IL', 'state_name': 'Illinois', 'state_slug': 'illinois', 'count': 100},
        {'city': 'Houston', 'state': 'TX', 'state_name': 'Texas', 'state_slug': 'texas', 'count': 90},
        {'city': 'Phoenix', 'state': 'AZ', 'state_name': 'Arizona', 'state_slug': 'arizona', 'count': 80},
        {'city': 'Philadelphia', 'state': 'PA', 'state_name': 'Pennsylvania', 'state_slug': 'pennsylvania', 'count': 75},
        {'city': 'San Antonio', 'state': 'TX', 'state_name': 'Texas', 'state_slug': 'texas', 'count': 70},
        {'city': 'San Diego', 'state': 'CA', 'state_name': 'California', 'state_slug': 'california', 'count': 65},
        {'city': 'Dallas', 'state': 'TX', 'state_name': 'Texas', 'state_slug': 'texas', 'count': 60},
        {'city': 'San Jose', 'state': 'CA', 'state_name': 'California', 'state_slug': 'california', 'count': 55}
    ]
    
    top_cities = []
    for city_info in sample_cities:
        top_cities.append({
            'city': city_info['city'],
            'state': city_info['state'],
            'state_name': city_info['state_name'],
            'state_slug': city_info['state_slug'],
            'city_slug': generate_seo_url(city_info['city']),
            'count': city_info['count']
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
    # For Vercel deployment, use sample data
    sample_cities = [
        {'city': 'New York', 'state': 'NY', 'state_name': 'New York', 'state_slug': 'new-york', 'count': 150},
        {'city': 'Los Angeles', 'state': 'CA', 'state_name': 'California', 'state_slug': 'california', 'count': 120},
        {'city': 'Chicago', 'state': 'IL', 'state_name': 'Illinois', 'state_slug': 'illinois', 'count': 100},
        {'city': 'Houston', 'state': 'TX', 'state_name': 'Texas', 'state_slug': 'texas', 'count': 90},
        {'city': 'Phoenix', 'state': 'AZ', 'state_name': 'Arizona', 'state_slug': 'arizona', 'count': 80}
    ]
    
    sample_states = [
        {'state': 'CA', 'state_name': 'California', 'state_slug': 'california', 'count': 500},
        {'state': 'TX', 'state_name': 'Texas', 'state_slug': 'texas', 'count': 450},
        {'state': 'NY', 'state_name': 'New York', 'state_slug': 'new-york', 'count': 400},
        {'state': 'FL', 'state_name': 'Florida', 'state_slug': 'florida', 'count': 350},
        {'state': 'IL', 'state_name': 'Illinois', 'state_slug': 'illinois', 'count': 300}
    ]
    
    # Process cities data
    all_cities = []
    for city_info in sample_cities:
        all_cities.append({
            'city': city_info['city'],
            'state': city_info['state'],
            'state_name': city_info['state_name'],
            'state_slug': city_info['state_slug'],
            'city_slug': generate_seo_url(city_info['city']),
            'count': city_info['count']
        })
    
    # Process states data
    all_states = []
    for state_info in sample_states:
        all_states.append({
            'state': state_info['state'],
            'state_name': state_info['state_name'],
            'state_slug': state_info['state_slug'],
            'count': state_info['count']
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
    # For Vercel deployment, return sample data
    sample_cities = [
        {'city': 'New York', 'state': 'NY', 'postal_code': '10001'},
        {'city': 'Los Angeles', 'state': 'CA', 'postal_code': '90210'},
        {'city': 'Chicago', 'state': 'IL', 'postal_code': '60601'},
        {'city': 'Houston', 'state': 'TX', 'postal_code': '77001'},
        {'city': 'Phoenix', 'state': 'AZ', 'postal_code': '85001'}
    ]
    
    cities_list = []
    for city_info in sample_cities:
        cities_list.append({
            'city': city_info['city'],
            'state': city_info['state'],
            'postal_code': city_info['postal_code'],
            'city_slug': generate_seo_url(city_info['city']),
            'state_slug': next((slug for slug, info in states_data.items() if info['abbr'].lower() == city_info['state'].lower() or info['name'].lower() == city_info['state'].lower()), None)
        })
    
    return jsonify({
        'total_cities': len(cities_list),
        'cities': cities_list,
        'message': 'Using sample data for Vercel deployment'
    })

@app.route('/debug/states')
def debug_states():
    """Debug route to show states in the data"""
    # For Vercel deployment, return sample data
    sample_states = ['CA', 'TX', 'NY', 'FL', 'IL']
    
    return jsonify({
        'state_counts': {'CA': 500, 'TX': 450, 'NY': 400, 'FL': 350, 'IL': 300},
        'us_state_counts': {'CA': 500, 'TX': 450, 'NY': 400, 'FL': 350, 'IL': 300},
        'total_records': 2000,
        'sample_states': sample_states,
        'sample_us_states': sample_states,
        'message': 'Using sample data for Vercel deployment'
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

if __name__ == '__main__':
    # Load data on startup
    load_llc_data()
    app.run(debug=True, host='0.0.0.0', port=5000)

# Vercel deployment
app.debug = False
