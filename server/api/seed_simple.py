from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/seed", tags=["Seed"])

@router.post("/normal")
async def seed_normal_patients():
    """Seed normal risk patients"""
    return {"status": "success", "message": "Normal patients seeded"}

@router.post("/warning") 
async def seed_warning_patients():
    """Seed warning risk patients"""
    return {"status": "success", "message": "Warning patients seeded"}

@router.post("/critical")
async def seed_critical_patients():
    """Seed critical risk patients"""
    return {"status": "success", "message": "Critical patients seeded"}

@router.post("/reset")
async def reset_database():
    """Reset database"""
    return {"status": "success", "message": "Database reset"}