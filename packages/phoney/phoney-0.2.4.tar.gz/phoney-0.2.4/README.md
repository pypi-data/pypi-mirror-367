# 🌐 Phoney - Realistic Fake Data Generator

[![PyPI Version](https://img.shields.io/pypi/v/phoney?color=blue)](https://pypi.org/project/phoney/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/phoney)](https://pypi.org/project/phoney/)

Generate locale-aware fake personal data for testing, development, and anonymization. Perfect for populating databases and creating test users.

---

## ✨ Features

* **50+ locales** including `en_US`, `fr_FR`, `ja_JP`, `de_DE`
* **Complete profiles** with names, emails, phones, and birthdates
* **Gender-specific** name generation
* **Zero dependencies** — lightweight and fast

---

## 📦 Installation

```bash
pip install phoney
```

---

## 🚀 Basic Usage

```python
from phoney import Phoney

phoney = Phoney()

# Individual data
title = phoney.first_name(locale="it_IT")
print(title)  # → "Marco"

print(phoney.phone(locale="ja_JP"))  # → "+81 90-1234-5678"

# Complete profile
profile = phoney.profile(locale="es_ES")
print(profile)
```

---

## 📚 Key Methods

| Method         | Description               | Example Usage                 |
| -------------- | ------------------------- | ----------------------------- |
| `first_name()` | Generate first name       | `first_name(gender="female")` |
| `last_name()`  | Generate last name        | `last_name(locale="fr_FR")`   |
| `full_name()`  | Generate full name        | `full_name(gender="male")`    |
| `phone()`      | Generate phone number     | `phone(locale="en_US")`       |
| `email()`      | Generate email address    | `email(first_name="john")`    |
| `profile()`    | Generate complete profile | `profile(locale="de_DE")`     |

---

## 🧩 Profile Structure

```python
{
  'first_name': 'Sophie',
  'last_name': 'Martin',
  'gender': 'female',
  'age': 34,
  'birthdate': datetime.date(1990, 5, 12),
  'email': 'sophie.martin@example.fr',
  'phone': '+33 6 12 34 56 78',
  'locale': 'fr_FR'
}
```

---

## 🌍 Supported Locales

US, UK, Canada, France, Germany, Italy, Spain, Japan, Brazil, Russia, China + 40 more

---

## 📜 License

**MIT** — Free for commercial and personal use.

Developed by **rarfile** • [Report Issue](https://github.com/yourusername/phoney/issues)

---

### 🛠️ To use:

1. Copy this entire block.
2. Paste into your `README.md` file.
3. Replace the `[Report Issue]` link with your actual GitHub issue tracker.

---

### 📌 Key Features Recap:

* ✅ Modern design with clear emoji headers
* ✅ Responsive badges for version/license info
* ✅ Concise feature highlights
* ✅ Practical usage examples
* ✅ Quick-reference methods table
* ✅ Profile structure visualization
* ✅ Mobile-responsive layout
* ✅ PyPI-optimized formatting
* ✅ Professional yet concise content
