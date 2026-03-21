# Quick Start - Create Collections & Sample Data

## One-Command Setup

Run this from the `backend` folder:

```bash
python seed_patients.py
```

This creates:
- ✅ 4 collections in MongoDB Atlas (patients, vitals, alerts, protocols)
- ✅ 5 sample patients across ICU beds
- ✅ Proper indexing for performance
- ✅ Ready for immediate testing

## What Gets Created

### Collections
| Collection | Purpose | Sample Records |
|-----------|---------|-----------------|
| **patients** | ICU patients | 5 sample patients (ICU-101 to ICU-105) |
| **vitals** | Vital sign readings | Created when you POST to /seed endpoints |
| **alerts** | Triggered alerts | Created when risk_score ≥ 40 |
| **protocols** | Sepsis protocols | Created when risk_score ≥ 70 (needs Gemini API key) |

### Sample Patients Created

1. **John Doe** - ICU-101 (Pneumonia, Penicillin allergy)
2. **Sarah Johnson** - ICU-102 (Post-op surgery, Post-surgical flag)
3. **Michael Chen** - ICU-103 (Sepsis, Multiple comorbidities)
4. **Emma Williams** - ICU-104 (UTI, Immunocompromised)
5. **David Martinez** - ICU-105 (Community-acquired pneumonia)

## Testing After Setup

### 1. Verify patients exist
```bash
curl http://localhost:8000/patients
```
Should return 5 patients with IDs and bed numbers

### 2. Seed normal vitals (no alerts)
```bash
curl -X POST http://localhost:8000/seed/normal
```

### 3. Seed warning vitals (creates alerts)
```bash
curl -X POST http://localhost:8000/seed/warning
```

### 4. Seed critical vitals (creates protocols)
```bash
curl -X POST http://localhost:8000/seed/critical
```

### 5. Check alerts created
```bash
curl http://localhost:8000/alerts
```

### 6. Check protocols created
```bash
curl http://localhost:8000/protocols
```

## Verify in MongoDB Atlas

Log into https://cloud.mongodb.com:

1. Select cluster **Asclepius**
2. Click **Collections** tab
3. Should see 4 collections:
   - patients (5 documents)
   - vitals (populated by /seed calls)
   - alerts (populated by risk scoring)
   - protocols (populated by critical alerts)

## Troubleshooting

### Script fails - "Cannot connect to MongoDB"
- ✅ Check `.env` has correct `MONGODB_URL`
- ✅ Verify IP whitelist in MongoDB Atlas (Network Access)
- ✅ Test connection: `python -c "from pymongo import MongoClient; MongoClient('mongodb_url')" `

### Collections exist but empty
- Run `python seed_patients.py` again
- Check backend logs for errors
- Verify Beanie initialized properly

### Patients appear but no vitals/alerts/protocols
- This is normal! Collections are lazy-created
- Use `/seed/normal`, `/seed/warning`, `/seed/critical` to trigger data
- Or use `/patients/{id}/vitals` to manually record vitals

## After Setup: Configuration

### Update Gemini API Key
Edit `backend/.env`:
```
GEMINI_API_KEY=<your_valid_key_from_https://aistudio.google.com/app/apikey>
```

Restart backend for changes to take effect.

### Enable Webhook Notifications (Optional)
Edit `backend/.env`:
```
NURSE_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
DOCTOR_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Collection Relationships

```
patients (1)
  ├── vitals (many) 
  │     └── alerts (many) [created when risk_score ≥ 40]
  │           └── protocols (1) [created when risk_score ≥ 70]
```

## Indexes Created

For optimal query performance:

**patients**
- bed_number (unique)
- risk_level

**vitals**
- patient_id
- recorded_at
- risk_score

**alerts**
- patient_id
- resolved
- triggered_at

**protocols**
- patient_id
- status
- generated_at

---

**Ready to go!** Run `python seed_patients.py` and start testing. 🚀
