# src/adnus/__init__.py
"""
adnus (AdNuS): Advanced Number Systems.

A Python library for exploring number systems beyond the standard real and complex numbers.
"""

# main.py dosyasındaki ana sınıfları ve fonksiyonları buraya import et
from .main import (
    AdvancedNumber,
    BicomplexNumber,
    NeutrosophicNumber,
    NeutrosophicComplexNumber,
    NeutrosophicBicomplexNumber,
    HyperrealNumber,
    oresme_sequence,
    harmonic_numbers,
    binet_formula
)

# __all__ listesi, "from adnus import *" komutu kullanıldığında nelerin import edileceğini tanımlar.
# Bu, kütüphanenizin genel arayüzünü (public API) belirlemek için iyi bir pratiktir.
__all__ = [
    "AdvancedNumber",
    "BicomplexNumber",
    "NeutrosophicNumber",
    "NeutrosophicComplexNumber",
    "NeutrosophicBicomplexNumber",
    "HyperrealNumber",
    "oresme_sequence",
    "harmonic_numbers",
    "binet_formula"
]
