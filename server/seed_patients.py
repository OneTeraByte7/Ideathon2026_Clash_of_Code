"""
Quick MongoDB collection initialization.
Run: python seed_patients.py
"""
import sys
import asyncio
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Change to backend directory for proper .env loading
os.chdir(backend_path)

from db.mongo_database import init_db, close_db
from models.patient import Patient


async def main():
    await init_db()
    print("✅ MongoDB Atlas connection successful")
    print("✅ Collections initialized")
    
    # Create sample patients
    samples = [
        {"name": "John Doe", "age": 65, "gender": "Male", "bed_number": "ICU-101", "diagnosis": "Pneumonia", "allergies": "Penicillin", "comorbidities": "Diabetes, HTN", "is_post_surgical": False, "is_immunocompromised": False},
        {"name": "Sarah Johnson", "age": 52, "gender": "Female", "bed_number": "ICU-102", "diagnosis": "Post-op surgery", "allergies": "", "comorbidities": "Asthma", "is_post_surgical": True, "is_immunocompromised": False},
        {"name": "Michael Chen", "age": 71, "gender": "Male", "bed_number": "ICU-103", "diagnosis": "Sepsis", "allergies": "Sulfa", "comorbidities": "COPD, CKD", "is_post_surgical": False, "is_immunocompromised": False},
        {"name": "Emma Williams", "age": 58, "gender": "Female", "bed_number": "ICU-104", "diagnosis": "UTI", "allergies": "", "comorbidities": "HIV+", "is_post_surgical": False, "is_immunocompromised": True},
        {"name": "David Martinez", "age": 73, "gender": "Male", "bed_number": "ICU-105", "diagnosis": "CAP", "allergies": "ACE inhibitors", "comorbidities": "CHF, AFib", "is_post_surgical": False, "is_immunocompromised": False},
    ]
    
    print("\n📝 Creating sample patients...")
    for data in samples:
        p = Patient(**data)
        await p.insert()
        print(f"✅ {p.name} - Bed {p.bed_number}")
    
    await close_db()
    print(f"\n✅ Created {len(samples)} patients in MongoDB Atlas")
    print("✅ All 4 collections ready: patients, vitals, alerts, protocols")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check MONGODB_URL in backend/.env is correct")
        print("2. Verify IP whitelist in MongoDB Atlas Network Access")
        print("3. Ensure MongoDB cluster is running")

