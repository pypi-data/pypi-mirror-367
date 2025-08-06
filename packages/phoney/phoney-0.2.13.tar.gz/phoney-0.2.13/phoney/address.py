# phoney/address.py
__all__ = ['generate_address']
"""Address generator with postal codes using real-world data."""

import random
import requests

_COUNTRY_DATA = None

def _get_country_data():
    """Fetch real country data (cached)"""
    global _COUNTRY_DATA
    if _COUNTRY_DATA is None:
        response = requests.get("https://restcountries.com/v3.1/all")
        _COUNTRY_DATA = response.json()
    return _COUNTRY_DATA

def generate_address(locale='en_US'):
    """Generate a fake address dictionary for the given locale."""
    from .data_loader import load_countries, load_streets, load_cities, load_states
    
    try:
        countries = load_countries()
        # Extract country codes and names
        country_codes = list(countries.keys())
        country_names = list(countries.values())
        
        # Get country code from locale
        country_code = locale.split('_')[-1] if '_' in locale else locale
        
        # Use locale-based country if available, otherwise random
        if country_code in country_codes:
            country = countries[country_code]
        else:
            country = random.choice(country_names)
        
        streets = load_streets().get(locale, ["Main Street"])
        cities = load_cities().get(locale, ["Metropolis"])
        states = load_states().get(locale, ["State"])
        
        return {
            'street': f"{random.randint(1, 999)} {random.choice(streets)}",
            'city': random.choice(cities),
            'state': random.choice(states),
            'postal_code': str(random.randint(10000, 99999)),
            'country': country
        }
    except Exception as e:
        return {
            'street': f"{random.randint(1, 999)} Wannock Street",
            'city': "Anytown",
            'state': "CA",
            'postal_code': str(random.randint(10000, 99999)),
            'country': "United States"
        }