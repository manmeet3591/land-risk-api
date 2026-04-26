import csv
import os
from typing import Dict, Any

class SpatialEngine:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "..", "data", "biophysical_table.csv")
        self.biophysical_data = self._load_data()

    def _load_data(self) -> Dict[str, Dict[str, float]]:
        data = {}
        with open(self.data_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data[row['name'].lower()] = {
                    'c_stock': float(row['c_stock']),
                    'biodiversity': float(row['biodiversity']),
                    'food_security': float(row['food_security'])
                }
        return data

    def calculate_tradeoffs(self, lat: float, lng: float, proposed_use: str) -> Dict[str, Any]:
        # Simulating a spatial lookup.
        # In a real tool, we would hit a GeoTIFF raster here based on coordinates.
        # For now, we'll assume a "Current Use" based on latitude or just default to Cropland.
        current_use = "cropland"
        if 0 <= lat <= 15: # Simulating Amazon-ish latitude
            current_use = "primary forest"
            
        current_metrics = self.biophysical_data.get(current_use.lower())
        proposed_metrics = self.biophysical_data.get(proposed_use.lower())

        if not current_metrics or not proposed_metrics:
            raise ValueError(f"Invalid land use types: {current_use} or {proposed_use}")

        # Normalize scores to -1 to 1 range for the "delta"
        # Carbon: Max is 280, we'll normalize delta by that
        carbon_delta = (proposed_metrics['c_stock'] - current_metrics['c_stock']) / 280.0
        bio_delta = proposed_metrics['biodiversity'] - current_metrics['biodiversity']
        food_delta = proposed_metrics['food_security'] - current_metrics['food_security']

        return {
            "current_use": current_use,
            "tradeoff_vector": {
                "carbon_score": round(carbon_delta, 2),
                "biodiversity_score": round(bio_delta, 2),
                "food_security_score": round(food_delta, 2)
            },
            "confidence": 0.85, # Increased confidence since we use real tables
            "red_flags": self._generate_red_flags(current_use, proposed_use, food_delta, bio_delta),
            "recommendation": self._generate_recommendation(proposed_use, food_delta)
        }

    def _generate_red_flags(self, cur, prop, food_d, bio_d):
        flags = []
        if food_d < -0.4:
            flags.append("Significant loss of local food production area")
        if bio_d < -0.3:
            flags.append("High risk to local wildlife and ecosystem intactness")
        if cur == "primary forest" and prop != "primary forest":
            flags.append("Critical: Project involves conversion of primary forest")
        return flags

    def _generate_recommendation(self, prop, food_d):
        if food_d < -0.3 and prop == "reforested land":
            return "Consider Agroforestry instead to maintain some food security while gaining carbon."
        if prop == "bioenergy crop":
            return "Ensure minimal nitrogen runoff to protect local water systems."
        return "Proceed with caution; verify local land rights before acquisition."
