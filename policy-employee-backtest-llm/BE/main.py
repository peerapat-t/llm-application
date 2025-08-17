# main.py
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd

# Import only the core simulation logic
from policy_backtest import run_policy_simulation

app = FastAPI(
    title="Policy Simulation API",
    description="An API to simulate employee feedback on new company policies."
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PolicyRequest(BaseModel):
    """Defines the structure for the incoming policy text."""
    policy_text: str

class SimulationResult(BaseModel):
    """Defines the structure for the simulation response."""
    data: List[Dict]
    policy_text: str

@app.post("/run-simulation/", response_model=SimulationResult)
async def run_simulation_endpoint(request: PolicyRequest):
    """
    Triggers the simulation for a given policy text sent in the request body.
    """
    try:
        results_df = run_policy_simulation(request.policy_text)
        
        # Convert NaN to None for JSON compatibility
        results_df = results_df.where(pd.notnull(results_df), None)
        
        return {
            "data": results_df.to_dict(orient="records"),
            "policy_text": request.policy_text
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)