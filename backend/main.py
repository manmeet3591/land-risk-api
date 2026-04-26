from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from services.spatial_engine import SpatialEngine

app = FastAPI(title="Land Risk API")
spatial_engine = SpatialEngine()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioRequest(BaseModel):
    lat: float
    lng: float
    proposed_use: str
    area_hectares: float

class TradeoffVector(BaseModel):
    carbon_score: float
    biodiversity_score: float
    food_security_score: float

class ScenarioResponse(BaseModel):
    current_use: str
    tradeoff_vector: TradeoffVector
    confidence: float
    red_flags: List[str]
    recommendation: str

@app.on_event("startup")
async def startup_event():
    print("✅ Land Risk Science Engine (InVEST) Initialized")
    print("🚀 API live at http://localhost:8000")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/v1/score-scenario", response_model=ScenarioResponse)
async def score_scenario(request: ScenarioRequest):
    try:
        result = spatial_engine.calculate_tradeoffs(
            lat=request.lat, 
            lng=request.lng, 
            proposed_use=request.proposed_use
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
