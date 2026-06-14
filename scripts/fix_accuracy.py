#!/usr/bin/env python3
"""Add ol and en accuracy entries to ACCURACY_DATA in HTML."""
import os, re

path = os.path.join(os.path.dirname(__file__), '..', 'prode-mundial-2026.html')

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the accuracy data section
# Pattern: after "pm" entry in sources, but before the closing of sources
# The current end looks like: "pm: {...}}, "weights_before": ...
# We need to add ol and en inside the sources object

# Add ol entry after pm in sources
ol_entry = ', "ol": {"label": "Olor\u00e1culo", "exact_accuracy": 0.0, "winner_accuracy": 0.0, "confidence_index": 0.0, "confidence_weighted": 0.0, "samples": 0, "exact_hits": 0, "winner_hits": 0, "current_weight": 3.0, "calibration_curve": [], "goal_bias_home": 0.0, "goal_bias_away": 0.0, "draw_frequency": 0.0, "actual_draw_frequency": 0.0}'
en_entry = ', "en": {"label": "Engine", "exact_accuracy": 0.0, "winner_accuracy": 0.0, "confidence_index": 0.0, "confidence_weighted": 0.0, "samples": 0, "exact_hits": 0, "winner_hits": 0, "current_weight": 1.5, "calibration_curve": [], "goal_bias_home": 0.0, "goal_bias_away": 0.0, "draw_frequency": 0.0, "actual_draw_frequency": 0.0}'

# Insert ol and en after the pm entry (before the closing of sources: `}}`)
old = '"pm": {"label": "Polymarket", "exact_accuracy": 16.7, "winner_accuracy": 50.0... (line truncated to 2000 chars)'

# Strategy: find the unique marker before and after the pm entry insertion point
# Look for: `"samples": 6}}, "weights_before":`
# This marks the end of... wait, no. The pm entry has `"samples": 6}}, "weights_before":` 
# Actually looking at the data: `"pm": {"goal_bias_home": -1.17, "goal_bias_away": -0.5, "draw_frequency": 33.3, "actual_draw_frequency": 50.0, "samples": 6}}, "weights_before":`

# So the sources structure is: {c: ..., g: ..., ..., pm: {..., samples: 6}}, "weights_before": {...
# I need to insert after `, "pm": {..., samples: 6}}` but before `, "weights_before": `

# Let me find the unique pattern
marker = '"actual_draw_frequency": 50.0, "samples": 6}}'
replacement = '"actual_draw_frequency": 50.0, "samples": 6}' + ol_entry + en_entry + '}'

if marker + ', "weights_before"' in html:
    html = html.replace(marker + ', "weights_before"', replacement + ', "weights_before"')
    print("Added ol and en to ACCURACY_DATA")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Written successfully")
else:
    print("Marker not found, trying alternative...")
    # Try reading the actual content more carefully
    idx = html.find('"pm": {"label": "Polymarket"')
    if idx > 0:
        # Find where this pm entry ends and weights_before starts
        end_marker = ', "weights_before":'
        end_idx = html.find(end_marker, idx)
        if end_idx > 0:
            pm_end = html.rfind('}', idx, end_idx) + 1  # include the closing }
            # Check if it's double }} (closing sources AND pm object)
            # Look for `}}`
            new_html = html[:pm_end] + ol_entry + en_entry + html[pm_end:]
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print("Added ol and en via index-based approach")
        else:
            print("Could not find weights_before marker")
    else:
        print("Could not find pm entry at all")
