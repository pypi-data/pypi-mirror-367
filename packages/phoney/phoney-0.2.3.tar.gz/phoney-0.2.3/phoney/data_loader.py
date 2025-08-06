# phoney/data_loader.py
"""Data loader for locale-specific information."""
import os
import importlib.resources as pkg_resources
import random
import json
from collections import defaultdict

DATA_PACKAGE = 'phoney.data.name_data'

def get_available_locales():
    """Get all available locales from the name_data directory."""
    locales = []
    with pkg_resources.files(DATA_PACKAGE) as base:
        for region in base.iterdir():
            if region.is_dir():
                for locale in region.iterdir():
                    if locale.is_dir():
                        locales.append(locale.name)
    return locales

def load_names(locale):
    """Load names for a specific locale."""
    names = {'male': [], 'female': [], 'last': []}
    with pkg_resources.files(DATA_PACKAGE) as base:
        for region in base.iterdir():
            locale_dir = region / locale
            if locale_dir.is_dir():
                for gender in names.keys():
                    file_path = locale_dir / f"{gender}.txt"
                    if file_path.is_file():
                        with file_path.open('r', encoding='utf-8') as f:
                            names[gender] = [line.strip() for line in f if line.strip()]
                break
    return names

def load_phone_formats():
    """Load phone number formats from JSON file."""
    with pkg_resources.files('phoney.data') as data_pkg:
        formats_path = data_pkg / 'phone_formats.json'
        with formats_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    with open(formats_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_email_domains():
    """Load email domains from JSON file."""
    domains_path = os.path.join(os.path.dirname(__file__), 'data', 'email_domains.json')
    with open(domains_path, 'r', encoding='utf-8') as f:
        return json.load(f)