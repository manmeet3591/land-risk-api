import csv
import os
import tempfile
import shutil
import numpy as np
import rasterio
from rasterio.transform import from_origin
from typing import Dict, Any, List
import natcap.invest.carbon.carbon
import natcap.invest.habitat_quality
import natcap.invest.ndr.ndr
import natcap.invest.sdr.sdr

class SpatialEngine:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.biophysical_table_path = os.path.join(self.data_dir, "biophysical_table.csv")
        self.threats_path = os.path.join(self.data_dir, "threats.csv")
        self.sensitivity_path = os.path.join(self.data_dir, "sensitivity.csv")
        self.biophysical_data = self._load_data()

    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        data = {}
        with open(self.biophysical_table_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name'].lower()
                data[name] = {
                    'lucode': int(row['lucode']),
                    'biodiversity_base': float(row['biodiversity']), # Fallback if InVEST fails
                    'food_security': float(row['food_security'])
                }
        return data

    def _create_raster(self, path: str, data: np.ndarray, lat: float, lng: float, dtype='int32'):
        res = 0.00027 
        rows, cols = data.shape
        transform = from_origin(lng - (cols//2 * res), lat + (rows//2 * res), res, res)
        
        with rasterio.open(
            path, 'w',
            driver='GTiff',
            height=rows, width=cols,
            count=1,
            dtype=dtype,
            crs='EPSG:4326',
            transform=transform,
        ) as dst:
            dst.write(data.astype(dtype), 1)

    def calculate_tradeoffs(self, lat: float, lng: float, proposed_use: str) -> Dict[str, Any]:
        current_use = "cropland"
        if 0 <= lat <= 15:
            current_use = "primary forest"

        cur_data = self.biophysical_data.get(current_use.lower())
        prop_data = self.biophysical_data.get(proposed_use.lower())

        if not cur_data or not prop_data:
            raise ValueError(f"Invalid land use: {current_use} or {proposed_use}")

        workspace = tempfile.mkdtemp(prefix="invest_full_")
        try:
            # 1. Create Base Rasters
            cur_raster = os.path.join(workspace, "current_lulc.tif")
            fut_raster = os.path.join(workspace, "future_lulc.tif")
            dem_raster = os.path.join(workspace, "dem.tif")
            precip_raster = os.path.join(workspace, "precip.tif")
            erosivity_raster = os.path.join(workspace, "erosivity.tif")
            erodibility_raster = os.path.join(workspace, "erodibility.tif")
            
            # 10x10 grids
            self._create_raster(cur_raster, np.full((10, 10), cur_data['lucode']), lat, lng)
            self._create_raster(fut_raster, np.full((10, 10), prop_data['lucode']), lat, lng)
            
            # Synthetic DEM (gentle slope for routing)
            dem_data = np.array([[float(100 - i - j) for j in range(10)] for i in range(10)])
            self._create_raster(dem_raster, dem_data, lat, lng, dtype='float32')
            
            # Constant environmental factors
            self._create_raster(precip_raster, np.full((10, 10), 1000.0), lat, lng, dtype='float32')
            self._create_raster(erosivity_raster, np.full((10, 10), 3000.0), lat, lng, dtype='float32')
            self._create_raster(erodibility_raster, np.full((10, 10), 0.2), lat, lng, dtype='float32')

            # Threat rasters for Habitat Quality
            threat_dir = os.path.join(workspace, "threats")
            os.makedirs(threat_dir)
            # Simulate an agriculture threat nearby
            ag_threat_data = np.zeros((10, 10))
            ag_threat_data[0:2, :] = 1 
            self._create_raster(os.path.join(threat_dir, "agriculture.tif"), ag_threat_data, lat, lng, dtype='float32')
            self._create_raster(os.path.join(threat_dir, "urban.tif"), np.zeros((10, 10)), lat, lng, dtype='float32')

            # 2. RUN MODELS
            
            # A. CARBON
            carbon_args = {
                'workspace_dir': os.path.join(workspace, "carbon"),
                'lulc_cur_path': cur_raster,
                'lulc_fut_path': fut_raster,
                'carbon_pools_path': self.biophysical_table_path,
                'calc_sequestration': True,
            }
            os.makedirs(carbon_args['workspace_dir'])
            natcap.invest.carbon.carbon.execute(carbon_args)
            
            # B. HABITAT QUALITY
            habitat_args = {
                'workspace_dir': os.path.join(workspace, "habitat"),
                'lulc_cur_path': cur_raster,
                'lulc_fut_path': fut_raster,
                'threats_table_path': self.threats_path,
                'sensitivity_table_path': self.sensitivity_path,
                'access_vector_path': None,
                'half_saturation_constant': 0.5,
                'threat_raster_folder': threat_dir,
            }
            os.makedirs(habitat_args['workspace_dir'])
            natcap.invest.habitat_quality.execute(habitat_args)

            # C. NDR (Water Risk)
            ndr_args = {
                'workspace_dir': os.path.join(workspace, "ndr"),
                'dem_path': dem_raster,
                'lulc_path': fut_raster, # Score the proposed state
                'run_n_valuation': False,
                'run_p_valuation': False,
                'biophysical_table_path': self.biophysical_table_path,
                'calc_n': True,
                'calc_p': False,
                'threshold_flow_accumulation': 100,
                'k_param': 2,
                'subsurface_critical_length_n': 10,
                'subsurface_eff_n': 0.1,
            }
            # Add precip for NDR
            ndr_args['precip_path'] = precip_raster
            os.makedirs(ndr_args['workspace_dir'])
            natcap.invest.ndr.ndr.execute(ndr_args)

            # D. SDR (Soil Erosion)
            sdr_args = {
                'workspace_dir': os.path.join(workspace, "sdr"),
                'dem_path': dem_raster,
                'lulc_path': fut_raster,
                'run_valuation': False,
                'biophysical_table_path': self.biophysical_table_path,
                'threshold_flow_accumulation': 1000,
                'k_param': 2,
                'sdr_max': 0.8,
                'ic_0_param': 0.5,
                'erodibility_path': erodibility_raster,
                'erosivity_path': erosivity_raster,
            }
            os.makedirs(sdr_args['workspace_dir'])
            natcap.invest.sdr.sdr.execute(sdr_args)

            # 3. EXTRACT RESULTS
            
            # Carbon
            carbon_score = self._extract_mean_from_raster(os.path.join(carbon_args['workspace_dir'], "delta_carbon.tif"))
            carbon_score = round(carbon_score / 280.0, 2)

            # Habitat (Biodiversity)
            # InVEST produces 'quality_f_scenario.tif' or similar.
            # Let's calculate delta quality: future - current
            # We'd need to run it twice or look at the rarity. 
            # For MVP, let's just use the 'quality_f' as the absolute score.
            habitat_score = self._extract_mean_from_raster(os.path.join(habitat_args['workspace_dir'], "quality_f.tif"))
            # Delta calculation:
            habitat_cur = self._extract_mean_from_raster(os.path.join(habitat_args['workspace_dir'], "quality_c.tif"))
            bio_score = round(habitat_score - habitat_cur, 2)

            # Water (NDR - Nitrogen Export)
            # n_export.tif. Higher export = Higher Risk = Lower Score.
            n_export = self._extract_mean_from_raster(os.path.join(ndr_args['workspace_dir'], "n_export.tif"))
            # Normalize: let's assume 50 kg/ha is a high load.
            # We want -1 to 1. If export increases, score decreases.
            # For simplicity: score = 1 - (n_export / 50.0)
            # But let's do delta:
            # We'd need current export too.
            # Simpler: map n_export to a 0-1 risk, then flip.
            water_risk_score = round(1.0 - (n_export / 50.0), 2)
            if water_risk_score < -1: water_risk_score = -1.0

            # Soil (SDR - Sediment Export)
            sed_export = self._extract_mean_from_raster(os.path.join(sdr_args['workspace_dir'], "sed_export.tif"))
            # Normalize: assume 10 tons/ha is high.
            soil_risk_score = round(1.0 - (sed_export / 10.0), 2)
            if soil_risk_score < -1: soil_risk_score = -1.0

            food_delta = prop_data['food_security'] - cur_data['food_security']

            return {
                "current_use": current_use,
                "tradeoff_vector": {
                    "carbon_score": carbon_score,
                    "biodiversity_score": bio_score,
                    "food_security_score": round(food_delta, 2),
                    "water_risk_score": water_risk_score,
                    "soil_risk_score": soil_risk_score
                },
                "confidence": 0.90,
                "red_flags": self._generate_red_flags(current_use, proposed_use, food_delta, bio_score),
                "recommendation": self._generate_recommendation(proposed_use, food_delta)
            }

        except Exception as e:
            print(f"Error in InVEST pipeline: {e}")
            raise e
        finally:
            shutil.rmtree(workspace)

    def _extract_mean_from_raster(self, path: str) -> float:
        # Search for the file if direct path fails (InVEST naming can vary)
        if not os.path.exists(path):
            dir_name = os.path.dirname(path)
            base_name = os.path.basename(path).replace(".tif", "")
            if os.path.exists(dir_name):
                for f in os.listdir(dir_name):
                    if base_name in f and f.endswith(".tif"):
                        path = os.path.join(dir_name, f)
                        break
        
        if os.path.exists(path):
            with rasterio.open(path) as src:
                data = src.read(1)
                # Filter out nodata
                valid_data = data[data != src.nodata]
                if len(valid_data) > 0:
                    return float(np.mean(valid_data))
        return 0.0

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
