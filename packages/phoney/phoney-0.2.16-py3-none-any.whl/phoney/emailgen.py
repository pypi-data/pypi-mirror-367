__all__ = ['generate_email']
"""Email address generator."""
import random
import re
from datetime import datetime
from .data_loader import load_email_domains

def generate_email(first_name=None, last_name=None, locale='en_US', age=None, birth_year=None, domain=None):
    if not first_name or not last_name:
        from .person import generate_person
        person = generate_person(locale)
        first_name = person['first_name']
        last_name = person['last_name']

    clean_first = re.sub(r'[^a-zA-Z]', '', first_name).lower() or "user"
    clean_last = re.sub(r'[^a-zA-Z]', '', last_name).lower() or "name"

    nickname = clean_first[:random.randint(3, min(5, len(clean_first)))] if len(clean_first) > 3 else clean_first
    initials = clean_first[0] + clean_last[0]

    if random.random() < 0.2 and clean_first.endswith(('y', 'ie')):
        nickname = clean_first.rstrip('yie') + 'ey'

    if not domain:
        try:
            domains = load_email_domains().get(locale, ["gmail.com"])
        except:
            domains = ["gmail.com"]
        domain = random.choice(domains)

    sep_choices = ['', '.', '_']
    sep = random.choices(sep_choices, weights=[2, 5, 3], k=1)[0]

    current_year = datetime.now().year
    if age is None and birth_year is not None:
        age = current_year - birth_year
    elif age is None:
        age = random.randint(13, 65)
    if birth_year is None:
        birth_year = current_year - age

    suffix_type = random.choice(['year', 'age', 'number', 'none'])
    if suffix_type == 'year':
        suffix = str(birth_year) if random.random() < 0.5 else str(birth_year)[-2:]
    elif suffix_type == 'age':
        suffix = str(age)
    elif suffix_type == 'number':
        suffix = str(random.randint(1, 19999))
    else:
        suffix = ''

    patterns = [
        f"{clean_first}{sep}{clean_last}{suffix}@{domain}",
        f"{clean_first[0]}{sep}{clean_last}{suffix}@{domain}",
        f"{clean_first}{clean_last}{suffix}@{domain}",
        f"{clean_first[0]}{clean_last}{suffix}@{domain}",
        f"{clean_first}{sep}{clean_last}@{domain}",
        f"{clean_first}{clean_last}@{domain}",
        f"{clean_first[0]}{sep}{clean_last}@{domain}",
        f"{clean_first}{clean_last[0]}@{domain}",
        f"{initials}{suffix}@{domain}",
        f"{nickname}{sep}{clean_last}{suffix}@{domain}",
        f"{clean_last}{sep}{clean_first}{suffix}@{domain}",
        f"{clean_first}{suffix}@{domain}",
        f"{nickname}{sep}{clean_last}@{domain}",
        f"{clean_last}{sep}{clean_first}@{domain}"
    ]

    return random.choice(patterns)