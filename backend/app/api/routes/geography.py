from fastapi import APIRouter
from typing import List
from app.services.geography_engine import geography_engine

router = APIRouter(prefix="/geography", tags=["Geography"])

@router.get("/countries")
async def get_countries():
    return {"countries": geography_engine.get_countries()}

@router.get("/states/{country}")
async def get_states(country: str):
    return {"states": geography_engine.get_states(country)}

@router.get("/cities/{country}/{state}")
async def get_cities(country: str, state: str):
    return {"cities": geography_engine.get_cities(country, state)}

@router.get("/ports/{country}/{state}/{city}")
async def get_ports(country: str, state: str, city: str):
    return {"ports": geography_engine.get_ports(country, state, city)}
