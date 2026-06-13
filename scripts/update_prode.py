#!/usr/bin/env python3
"""
Script para actualizar el HTML del Prode Mundial 2026 con predicciones adicionales
de modelos de simulacion masiva: Fansided, ESPN, Yahoo Sports.
"""

import re

# Datos de predicciones de las 3 fuentes adicionales para los 72 partidos
# fs = Fansided, esp = ESPN, yh = Yahoo Sports
additional_predictions = {
    # Group A
    1:  {"fs": "2-0",  "esp": "2-0",  "yh": "2-1"},   # Mexico vs South Africa
    2:  {"fs": "1-1",  "esp": "1-1",  "yh": "1-0"},   # South Korea vs Czechia
    3:  {"fs": "2-0",  "esp": "2-1",  "yh": "1-0"},   # Canada vs Bosnia (note: yh says 1-0, but match 3 is Canada vs Bosnia)
    4:  {"fs": "2-1",  "esp": "2-0",  "yh": "2-0"},   # USA vs Paraguay
    5:  {"fs": "0-2",  "esp": "0-2",  "yh": "0-2"},   # Qatar vs Switzerland
    6:  {"fs": "2-0",  "esp": "0-1",  "yh": "0-0"},   # Brazil vs Morocco
    7:  {"fs": "0-2",  "esp": "1-2",  "yh": "1-3"},   # Haiti vs Scotland
    8:  {"fs": "0-2",  "esp": "1-1",  "yh": "0-2"},   # Australia vs Turkiye
    9:  {"fs": "4-0",  "esp": "5-0",  "yh": "3-0"},   # Germany vs Curacao
    10: {"fs": "2-1",  "esp": "2-1",  "yh": "1-2"},   # Netherlands vs Japan
    11: {"fs": "1-2",  "esp": "0-1",  "yh": "0-1"},   # Ivory Coast vs Ecuador
    12: {"fs": "2-0",  "esp": "2-1",  "yh": "2-1"},   # Sweden vs Tunisia
    13: {"fs": "3-0",  "esp": "5-0",  "yh": "5-0"},   # Spain vs Cape Verde
    14: {"fs": "2-1",  "esp": "2-1",  "yh": "3-0"},   # Belgium vs Egypt
    15: {"fs": "0-2",  "esp": "0-2",  "yh": "0-2"},   # Saudi Arabia vs Uruguay
    16: {"fs": "2-0",  "esp": "1-1",  "yh": "1-0"},   # Iran vs New Zealand
    17: {"fs": "3-1",  "esp": "2-1",  "yh": "4-1"},   # France vs Senegal
    18: {"fs": "0-3",  "esp": "0-2",  "yh": "0-5"},   # Iraq vs Norway
    19: {"fs": "2-0",  "esp": "1-0",  "yh": "1-0"},   # Argentina vs Algeria
    20: {"fs": "3-0",  "esp": "3-1",  "yh": "1-0"},   # Austria vs Jordan
    21: {"fs": "3-0",  "esp": "1-2",  "yh": "3-1"},   # Portugal vs DR Congo
    22: {"fs": "2-1",  "esp": "1-1",  "yh": "1-1"},   # England vs Croatia
    23: {"fs": "2-1",  "esp": "1-2",  "yh": "1-2"},   # Ghana vs Panama
    24: {"fs": "0-2",  "esp": "1-2",  "yh": "1-1"},   # Uzbekistan vs Colombia
    25: {"fs": "2-0",  "esp": "1-0",  "yh": "1-1"},   # Czechia vs South Africa
    26: {"fs": "2-0",  "esp": "2-1",  "yh": "1-0"},   # Switzerland vs Bosnia
    27: {"fs": "2-0",  "esp": "1-0",  "yh": "2-0"},   # Canada vs Qatar
    28: {"fs": "1-1",  "esp": "1-1",  "yh": "2-1"},   # Mexico vs South Korea
    29: {"fs": "2-0",  "esp": "1-1",  "yh": "2-1"},   # USA vs Australia
    30: {"fs": "0-2",  "esp": "0-0",  "yh": "1-2"},   # Scotland vs Morocco
    31: {"fs": "3-0",  "esp": "3-0",  "yh": "5-1"},   # Brazil vs Haiti
    32: {"fs": "2-1",  "esp": "1-2",  "yh": "2-0"},   # Turkiye vs Paraguay
    33: {"fs": "2-1",  "esp": "2-0",  "yh": "1-2"},   # Netherlands vs Sweden
    34: {"fs": "2-1",  "esp": "3-1",  "yh": "2-1"},   # Germany vs Ivory Coast
    35: {"fs": "3-0",  "esp": "2-0",  "yh": "2-0"},   # Ecuador vs Curacao
    36: {"fs": "0-2",  "esp": "0-1",  "yh": "0-1"},   # Tunisia vs Japan
    37: {"fs": "3-0",  "esp": "3-0",  "yh": "4-0"},   # Spain vs Saudi Arabia
    38: {"fs": "2-0",  "esp": "1-1",  "yh": "2-1"},   # Belgium vs Iran
    39: {"fs": "2-0",  "esp": "3-0",  "yh": "2-1"},   # Uruguay vs Cape Verde
    40: {"fs": "0-2",  "esp": "2-1",  "yh": "2-2"},   # New Zealand vs Egypt
    41: {"fs": "2-0",  "esp": "2-2",  "yh": "2-0"},   # Argentina vs Austria
    42: {"fs": "4-0",  "esp": "3-0",  "yh": "6-0"},   # France vs Iraq
    43: {"fs": "2-1",  "esp": "1-1",  "yh": "3-2"},   # Norway vs Senegal
    44: {"fs": "0-2",  "esp": "1-1",  "yh": "1-2"},   # Jordan vs Algeria
    45: {"fs": "3-0",  "esp": "2-1",  "yh": "1-1"},   # Portugal vs Uzbekistan
    46: {"fs": "3-1",  "esp": "3-0",  "yh": "3-0"},   # England vs Ghana
    47: {"fs": "1-2",  "esp": "1-2",  "yh": "2-0"},   # Panama vs Croatia
    48: {"fs": "2-0",  "esp": "1-0",  "yh": "4-0"},   # Colombia vs DR Congo
    49: {"fs": "2-1",  "esp": "1-1",  "yh": "2-1"},   # Switzerland vs Canada
    50: {"fs": "2-0",  "esp": "0-1",  "yh": "2-1"},   # Bosnia vs Qatar
    51: {"fs": "0-3",  "esp": "0-1",  "yh": "2-1"},   # Scotland vs Brazil
    52: {"fs": "2-0",  "esp": "2-0",  "yh": "2-0"},   # Morocco vs Haiti
    53: {"fs": "1-2",  "esp": "1-2",  "yh": "1-1"},   # Czechia vs Mexico
    54: {"fs": "0-2",  "esp": "1-2",  "yh": "1-3"},   # South Africa vs South Korea
    55: {"fs": "1-2",  "esp": "1-1",  "yh": "0-0"},   # Ecuador vs Germany
    56: {"fs": "0-2",  "esp": "1-3",  "yh": "1-2"},   # Curacao vs Ivory Coast
    57: {"fs": "2-1",  "esp": "1-1",  "yh": "0-1"},   # Japan vs Sweden
    58: {"fs": "0-3",  "esp": "0-3",  "yh": "4-2"},   # Tunisia vs Netherlands
    59: {"fs": "1-2",  "esp": "2-1",  "yh": "2-2"},   # Turkiye vs USA
    60: {"fs": "2-0",  "esp": "1-1",  "yh": "1-1"},   # Paraguay vs Australia
    61: {"fs": "0-2",  "esp": "1-1",  "yh": "3-2"},   # Norway vs France
    62: {"fs": "2-0",  "esp": "3-1",  "yh": "3-0"},   # Senegal vs Iraq
    63: {"fs": "1-0",  "esp": "2-1",  "yh": "1-1"},   # Cape Verde vs Saudi Arabia
    64: {"fs": "1-2",  "esp": "1-2",  "yh": "1-3"},   # Uruguay vs Spain
    65: {"fs": "1-0",  "esp": "0-0",  "yh": "1-0"},   # Egypt vs Iran
    66: {"fs": "0-3",  "esp": "1-2",  "yh": "1-3"},   # New Zealand vs Belgium
    67: {"fs": "0-3",  "esp": "0-2",  "yh": "1-2"},   # Panama vs England
    68: {"fs": "2-1",  "esp": "2-0",  "yh": "1-2"},   # Croatia vs Ghana
    69: {"fs": "1-2",  "esp": "2-0",  "yh": "3-3"},   # Colombia vs Portugal
    70: {"fs": "2-0",  "esp": "1-2",  "yh": "0-1"},   # DR Congo vs Uzbekistan
    71: {"fs": "0-2",  "esp": "1-1",  "yh": "1-1"},   # Algeria vs Austria
    72: {"fs": "0-3",  "esp": "0-3",  "yh": "0-4"},   # Jordan vs Argentina
}

print("Datos compilados para 72 partidos")
print(f"Total de predicciones: {len(additional_predictions)}")
