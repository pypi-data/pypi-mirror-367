__all__ = ['generate_profile']

import random
import uuid
from datetime import datetime
from .person import generate_person
from .phone import generate_phone
from .emailgen import generate_email
from .age import generate_age
from .agent import generate_user_agent
from .address import generate_address
from .data_loader import get_available_locales

def generate_profile(locale=None, gender=None, domain="example.com", uuid_version=4):
    """
    Generate a complete personal profile with enhanced details.
    
    Args:
        locale: Locale to use for generation (random if not specified)
        gender: Gender to use for generation (random if not specified)
        domain: Domain name for email generation
        uuid_version: UUID version (1, 3, 4, or 5)
        
    Returns:
        dict: Complete profile dictionary with all new fields
    """
    if locale is None:
        locale = random.choice(get_available_locales())
    
    person = generate_person(locale, gender)
    first_name = person['first_name']
    last_name = person['last_name']
    gender = person['gender']

    age, birthdate = generate_age()
    birth_year = birthdate.year

    phone = generate_phone(locale)
    email = generate_email(first_name, last_name, locale, domain=domain)
    
    user_agent = generate_user_agent()
    
    if uuid_version == 3 or uuid_version == 5:
        namespace = uuid.NAMESPACE_DNS
        name = f"{first_name}.{last_name}@{domain}"
        profile_uuid = str(uuid.uuid3(namespace, name)) if uuid_version == 3 else str(uuid.uuid5(namespace, name))
    elif uuid_version == 1:
        profile_uuid = str(uuid.uuid1())
    else: 
        profile_uuid = str(uuid.uuid4())

    address = generate_address(locale)
    
    created_at = datetime.now().isoformat()

    return {
        'uuid': profile_uuid,
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f"{first_name} {last_name}",
        'gender': gender,
        
        'age': age,
        'birthdate': birthdate.isoformat(),
        'birth_year': birth_year,
        
        'email': email,
        'phone': phone,
        'address': address,
        
        'user_agent': user_agent,
        'locale': locale,
        'created_at': created_at
    }