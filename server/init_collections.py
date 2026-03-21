"""
Initialize MongoDB collections and seed sample patients.
Run this once after connecting to MongoDB to create all collections.
"""
import asyncio
from datetime import datetime, timezone
from db.mongo_database import init_db, close_db
from models.patient import Patient
from models.vital import Vital
from models.alert import Alert
from models.protocol import Protocol


async def create_sample_patients():
    """Create sample patients for testing."""
    patients_data = [
        {
            "name": "John Doe",
            "age": 65,
            "gender": "Male",
            "bed_number": "ICU-101",
            "diagnosis": "Pneumonia suspected",
            "allergies": "Penicillin",
            "comorbidities": "Diabetes, Hypertension",
            "is_post_surgical": False,
            "is_immunocompromised": False,
        },
        {
            "name": "Sarah Johnson",
            "age": 52,
            "gender": "Female",
            "bed_number": "ICU-102",
            "diagnosis": "Post-op abdominal surgery",
            "allergies": "None",
            "comorbidities": "Asthma",
            "is_post_surgical": True,
            "is_immunocompromised": False,
        },
        {
            "name": "Michael Chen",
            "age": 71,
            "gender": "Male",
            "bed_number": "ICU-103",
            "diagnosis": "Sepsis suspected",
            "allergies": "Sulfa drugs",
            "comorbidities": "COPD, CKD stage 3",
            "is_post_surgical": False,
            "is_immunocompromised": False,
        },
        {
            "name": "Emma Williams",
            "age": 58,
            "gender": "Female",
            "bed_number": "ICU-104",
            "diagnosis": "Urinary tract infection",
            "allergies": "None",
            "comorbidities": "HIV+",
            "is_post_surgical": False,
            "is_immunocompromised": True,
        },
        {
            "name": "David Martinez",
            "age": 73,
            "gender": "Male",
            "bed_number": "ICU-105",
            "diagnosis": "Community-acquired pneumonia",
            "allergies": "ACE inhibitors",
            "comorbidities": "CHF, Atrial fibrillation",
            "is_post_surgical": False,
            "is_immunocompromised": False,
        },
    ]

    created_patients = []
    for data in patients_data:
        patient = Patient(**data)
        await patient.insert()
        created_patients.append(patient)
        print(f"✅ Created patient: {patient.name} (ID: {patient.id})")

    return created_patients


async def main():
    """Initialize MongoDB and create collections with sample data."""
    print("🔄 Initializing MongoDB connection...")
    await init_db()
    print("✅ MongoDB initialized")

    try:
        print("\n📝 Creating sample patients...")
        patients = await create_sample_patients()
        print(f"\n✅ Created {len(patients)} sample patients")

        print("\n📊 Collection Summary:")
        patient_count = len(await Patient.find_all().to_list())
        vital_count = len(await Vital.find_all().to_list())
        alert_count = len(await Alert.find_all().to_list())
        protocol_count = len(await Protocol.find_all().to_list())

        print(f"  - patients: {patient_count}")
        print(f"  - vitals: {vital_count}")
        print(f"  - alerts: {alert_count}")
        print(f"  - protocols: {protocol_count}")

        print("\n✅ All collections ready for use!")
        print("\n💡 Next steps:")
        print("  1. Use POST /seed/normal, /seed/warning, or /seed/critical to test")
        print("  2. View patients at GET /patients")
        print("  3. Monitor alerts at GET /alerts")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
