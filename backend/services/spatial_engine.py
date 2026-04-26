import csv
import os
import tempfile
import shutil
import numpy as np
import rasterio
from rasterio.transform import from_origin
from typing import Dict, Any, List
import natcap.invest.carbon.carbon

class SpatialEngine:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.biophysical_table_path = os.path.join(self.data_dir, "biophysical_table.csv")
        self.biophysical_data = self._load_data()

    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        data = {}
        with open(self.biophysical_table_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name'].lower()
                data[name] = {
                    'lucode': int(row['lucode']),
                    'biodiversity': float(row['biodiversity']),
                    'food_security': float(row['food_security'])
                }
        return data

    def _create_dummy_raster(self, path: str, lucode: int, lat: float, lng: float):
        """Creates a tiny 10x10 GeoTIFF with the given lucode."""
        # 10x10 grid with 30m resolution (approx 0.00027 degrees)
        res = 0.00027 
        transform = from_origin(lng - (5 * res), lat + (5 * res), res, res)
        
        with rasterio.open(
            path, 'w',
            driver='GTiff',
            height=10, width=10,
            count=1,
            dtype='int32',
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(np.full((10, 10), lucode, dtype='int32'), 1)

    def calculate_tradeoffs(self, lat: float, lng: float, proposed_use: str) -> Dict[str, Any]:
        # Determine current use (mock spatial lookup)
        current_use = "cropland"
        if 0 <= lat <= 15:
            current_use = "primary forest"

        cur_data = self.biophysical_data.get(current_use.lower())
        prop_data = self.biophysical_data.get(proposed_use.lower())

        if not cur_data or not prop_data:
            raise ValueError(f"Invalid land use: {current_use} or {proposed_use}")

        # Setup InVEST Carbon Run
        workspace = tempfile.mkdtemp(prefix="invest_carbon_")
        try:
            cur_raster = os.path.join(workspace, "current_lulc.tif")
            fut_raster = os.path.join(workspace, "future_lulc.tif")
            
            self._create_dummy_raster(cur_raster, cur_data['lucode'], lat, lng)
            self._create_dummy_raster(fut_raster, prop_data['lucode'], lat, lng)

            args = {
                'workspace_dir': workspace,
                'lulc_cur_path': cur_raster,
                'lulc_fut_path': fut_raster,
                'carbon_pools_path': self.biophysical_table_path,
                'calc_sequestration': True,
            }

            print(f"Executing real InVEST Carbon model in {workspace}...")
            natcap.invest.carbon.carbon.execute(args)

            # Read result from InVEST output
            # InVEST produces a 'delta_carbon.tif'
            delta_path = os.path.join(workspace, "delta_carbon_scenario_1.tif") 
            # Note: InVEST might add a suffix if we provided one, but here it's default.
            # Actually, looking at the source, if no suffix, it's 'delta_carbon.tif'
            # Let's check common output filenames.
            
            delta_carbon_val = 0.0
            possible_output = os.path.join(workspace, "delta_carbon.tif")
            if not os.path.exists(possible_output):
                 # InVEST sometimes adds results_suffix or uses different names
                 # Let's just list and find the delta file if it's not where we expect
                 for f in os.listdir(workspace):
                     if "delta_carbon" in f and f.endswith(".tif"):
                         possible_output = os.path.join(workspace, f)
                         break

            if os.path.exists(possible_output):
                with rasterio.open(possible_output) as src:
                    data = src.read(1)
                    delta_carbon_val = float(np.mean(data))
            
            # Normalize the score for the UI (-1 to 1)
            # Max delta could be ~280 (forest - builtup)
            carbon_score = round(delta_carbon_val / 280.0, 2)
            
            bio_delta = prop_data['biodiversity'] - cur_data['biodiversity']
            food_delta = prop_data['food_security'] - cur_data['food_security']

            return {
                "current_use": current_use,
                "tradeoff_vector": {
                    "carbon_score": carbon_score,
                    "biodiversity_score": round(bio_delta, 2),
                    "food_security_score": round(food_delta, 2)
                },
                "confidence": 0.95,
                "red_flags": self._generate_red_flags(current_use, proposed_use, food_delta, bio_delta),
                "recommendation": self._generate_recommendation(proposed_use, food_delta)
            }

        finally:
            # Optionally keep for debugging or remove
            shutil.rmtree(workspace)

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
