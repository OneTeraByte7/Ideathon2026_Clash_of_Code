from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/stats")
async def get_analytics_stats():
    """Get analytics statistics"""
    return {
        "total_patients": 2,
        "critical_patients": 1,
        "warning_patients": 1,
        "normal_patients": 0,
        "active_alerts": 2,
        "protocols_pending": 1,
        "average_risk_score": 61.85
    }