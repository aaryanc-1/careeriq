"""
Countries config — CareerIQ
-----------------------------
The English-speaking Adzuna markets we scrape, with their currency info
for honest, native-currency display (we never convert between currencies).

Each entry: code (Adzuna path code), name, currency_code, currency_symbol.
"""

COUNTRIES = [
    {"code": "us", "name": "United States", "currency": "USD", "symbol": "$",  "flag": "🇺🇸"},
    {"code": "gb", "name": "United Kingdom", "currency": "GBP", "symbol": "£",  "flag": "🇬🇧"},
    {"code": "ca", "name": "Canada",         "currency": "CAD", "symbol": "C$", "flag": "🇨🇦"},
    {"code": "au", "name": "Australia",      "currency": "AUD", "symbol": "A$", "flag": "🇦🇺"},
    {"code": "in", "name": "India",          "currency": "INR", "symbol": "₹",  "flag": "🇮🇳"},
    {"code": "nz", "name": "New Zealand",    "currency": "NZD", "symbol": "NZ$","flag": "🇳🇿"},
    {"code": "sg", "name": "Singapore",      "currency": "SGD", "symbol": "S$", "flag": "🇸🇬"},
]

# Quick lookups
BY_CODE = {c["code"]: c for c in COUNTRIES}

def country_codes():
    return [c["code"] for c in COUNTRIES]

def meta(code):
    return BY_CODE.get(code, {"code": code, "name": code.upper(),
                              "currency": "", "symbol": "", "flag": "🌍"})
