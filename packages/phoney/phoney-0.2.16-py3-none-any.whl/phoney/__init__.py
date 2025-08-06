__all__ = [
    'Phoney',
    'phoney',
    'generate_person',
    'generate_phone',
    'generate_email',
    'generate_age',
    'generate_profile',
    'generate_user_agent',
    'generate_uuid',
    'generate_address'
]

from .person import generate_person
from .phone import generate_phone
from .emailgen import generate_email
from .data_loader import load_email_domains, get_available_locales
from .age import generate_age
from .create_profile import generate_profile
from .agent import generate_user_agent
from .uuidgen import generate_uuid

class Phoney:
    """
    # from .address import generate_address (removed)

    Usage:
        from phoney import Phoney
        phoney = Phoney()
        phoney.first_name(gender="male", locale="en_GB")
        phoney.last_name(locale="fr_FR")
        phoney.phone(locale="en_US")
        phoney.email(first_name="jim", last_name="cooley", locale="en_US")
        phoney.profile(locale="de_DE")
    """
    def first_name(self, gender=None, locale='en_US'):
        """
        Generate a first name.
        Args:
            gender (str): 'male' or 'female'. If None, random.
            locale (str): Locale code (e.g. 'en_US').
        Returns:
            str: First name.
        """
        return generate_person(locale, gender)['first_name']

    def last_name(self, gender=None, locale='en_US'):
        """
        Generate a last name.
        Args:
            gender (str): 'male' or 'female'. If None, random.
            locale (str): Locale code.
        Returns:
            str: Last name.
        """
        return generate_person(locale, gender)['last_name']

    def full_name(self, gender=None, locale='en_US'):
        """
        Generate a full name.
        Args:
            gender (str): 'male' or 'female'. If None, random.
            locale (str): Locale code.
        Returns:
            str: Full name.
        """
        p = generate_person(locale, gender)
        return f"{p['first_name']} {p['last_name']}"

    def gender(self, locale='en_US'):
        """
        Generate a gender value.
        Args:
            locale (str): Locale code.
        Returns:
            str: Gender ('male' or 'female').
        """
        return generate_person(locale)['gender']

    def phone(self, locale='en_US'):
        """
        Generate a phone number for the given locale.
        Args:
            locale (str): Locale code.
        Returns:
            str: Phone number.
        """
        return generate_phone(locale)

    def email(self, first_name=None, last_name=None, locale='en_US', age=None, birth_year=None):
        """
        Generate a realistic email address.
        Args:
            first_name (str): First name. If None, random.
            last_name (str): Last name. If None, random.
            locale (str): Locale code.
            age (int): Age (optional).
            birth_year (int): Birth year (optional).
        Returns:
            str: Email address.
        """
        if not first_name or not last_name:
            p = generate_person(locale)
            first_name = p['first_name']
            last_name = p['last_name']
        return generate_email(first_name, last_name, locale, age=age, birth_year=birth_year)

    def age(self, min_age=18, max_age=80):
        """
        Generate a random age.
        Args:
            min_age (int): Minimum age.
            max_age (int): Maximum age.
        Returns:
            int: Age.
        """
        return generate_age(min_age, max_age)[0]

    def birthdate(self, min_age=18, max_age=80):
        """
        Generate a random birthdate.
        Args:
            min_age (int): Minimum age.
            max_age (int): Maximum age.
        Returns:
            datetime.date: Birthdate.
        """
        return generate_age(min_age, max_age)[1]

    def profile(self, locale='en_US', gender=None):
        """
        Generate a complete fake profile.
        Args:
            locale (str): Locale code.
            gender (str): 'male' or 'female'. If None, random.
        Returns:
            dict: Profile with name, gender, age, birthdate, email, phone, locale.
        """
        return generate_profile(locale, gender)

    def user_agent(self, device_type="desktop"):
        """
        Generate browser user agent string
        Args:
            device_type: 'desktop' or 'mobile'
        Returns:
            str: User agent string
        """
        return generate_user_agent(device_type)
    
    def uuid(self, version=4):
        """
        Generate UUID
        Args:
            version: UUID version (1,3,4,5)
        Returns:
            str: UUID string
        """
        return generate_uuid(version)
    
phoney = Phoney()