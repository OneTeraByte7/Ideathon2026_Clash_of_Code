from fastapi import APIRouter
import random

router = APIRouter()

HEALTH_TIPS = [
    "Stay hydrated by drinking enough water each day.",
    "Get at least 7-8 hours of sleep every night.",
    "Exercise regularly to maintain a healthy body and mind.",
    "Eat a balanced diet rich in fruits and vegetables.",
    "Take breaks and manage stress effectively.",
    "Wash your hands frequently to prevent illness.",
    "Avoid smoking and limit alcohol consumption.",
    "Practice mindfulness or meditation for mental well-being."
]

@router.get("/health-tip")
def get_health_tip():
    return {"tip": random.choice(HEALTH_TIPS)}
