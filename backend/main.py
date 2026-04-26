from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Land Risk API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioRequest(BaseModel):
    location: str
    current_use: str
    proposed_use: str
    area_hectares: float

class TradeoffVector(BaseModel):
    carbon_score: float
    biodiversity_score: float
    food_security_score: float

class ScenarioResponse(BaseModel):
    tradeoff_vector: TradeoffVector
    confidence: float
    red_flags: List[str]
    recommendation: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/v1/score-scenario", response_model=ScenarioResponse)
async def score_scenario(request: ScenarioRequest):
    # Mock data for initial frontend integration
    return ScenarioResponse(
        tradeoff_vector=TradeoffVector(
            carbon_score=0.85,
            biodiversity_score=0.42,
            food_security_score=-0.61
        ),
        confidence=0.78,
        red_flags=["High food production displacement detected"],
        recommendation="Consider agroforestry to mitigate food security loss."
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
