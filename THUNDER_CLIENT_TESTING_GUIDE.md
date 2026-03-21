# 🏥 Asclepius AI - Complete Thunder Client Testing Guide

## 📋 Table of Contents
1. [Setup & Prerequisites](#setup--prerequisites)
2. [Testing Flow Overview](#testing-flow-overview)
3. [Detailed Testing Steps](#detailed-testing-steps)
4. [Expected Responses](#expected-responses)
5. [Common Issues & Troubleshooting](#common-issues--troubleshooting)

---

## 🚀 Setup & Prerequisites

### 1. **Environment Setup**
Make sure your `.env` file has the Gemini API key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. **Start the Backend**
```bash
cd E:\Ideathon2026\backend
python -m db.init_db
uvicorn main:app --reload --port 8000
```

### 3. **Import Thunder Client Collection**
- Open VS Code
- Install Thunder Client extension
- Click Thunder Client icon → Collections → Menu (⋮) → Import
- Select `E:\Ideathon2026\thunder-collection.json`

---

## 🎯 Testing Flow Overview

```
1. Health Check → Verify server running
2. Create Patients → Add test patients to database
3. Seed Normal → Healthy vitals (no alerts)
4. Seed Warning → Borderline sepsis (nurse notification)
5. Seed Critical → Emergency sepsis (nurse + doctor + Gemini protocol)
6. View Alerts → Check generated alerts
7. View Protocols → See Gemini-generated treatment plans
8. Approve Protocol → Doctor reviews and approves
9. Analytics → View system performance
```

---

## 📝 Detailed Testing Steps

### **Step 1: Health Check** ✅

**Request:** `GET /health`

**What it tests:** Server is running

**Expected Response:**
```json
{
  "status": "healthy"
}
```

---

### **Step 2: Create Patients** 👥

**Request:** `POST /patients/`

**Body:**
```json
{
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "bed_number": "ICU-101",
  "diagnosis": "Sepsis suspected",
  "allergies": "Penicillin",
  "comorbidities": "Diabetes",
  "is_post_surgical": false,
  "is_immunocompromised": false
}
```

**What it tests:** Patient creation

**Expected Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "age": 45,
  "gender": "Male",
  "bed_number": "ICU-101",
  "diagnosis": "Sepsis suspected",
  "allergies": "Penicillin",
  "comorbidities": "Diabetes",
  "is_post_surgical": false,
  "is_immunocompromised": false,
  "risk_level": "normal",
  "current_risk_score": 0.0,
  "created_at": "2026-03-21T09:47:00.000Z",
  "updated_at": "2026-03-21T09:47:00.000Z"
}
```

**Action:** Create 2-3 patients for better testing

**Variations to try:**
```json
{
  "name": "Jane Smith",
  "age": 62,
  "gender": "Female",
  "bed_number": "ICU-102",
  "diagnosis": "Post-surgical infection",
  "allergies": "None",
  "comorbidities": "Hypertension, COPD",
  "is_post_surgical": true,
  "is_immunocompromised": false
}
```

```json
{
  "name": "Robert Johnson",
  "age": 38,
  "gender": "Male",
  "bed_number": "ICU-103",
  "diagnosis": "Pneumonia",
  "allergies": "Sulfa drugs",
  "comorbidities": "None",
  "is_post_surgical": false,
  "is_immunocompromised": true
}
```

---

### **Step 3: List All Patients** 📋

**Request:** `GET /patients/`

**What it tests:** Retrieve all patients

**Expected Response:** Array of all patients created

---

### **Step 4: Seed Normal Vitals** 🔵

**Request:** `POST /seed/normal`

**What it tests:** 
- Vitals ingestion
- Risk calculation
- Normal scenario (no alerts)

**Expected Response:**
```json
{
  "seeded": "normal",
  "description": "🔵 All patients showing healthy vitals. No alerts triggered.",
  "patients_updated": 3,
  "results": [
    {
      "patient_id": 1,
      "patient_name": "John Doe",
      "bed": "ICU-101",
      "risk_score": 12.5,
      "risk_level": "normal",
      "vitals": {
        "heart_rate": 75.0,
        "systolic_bp": 120.0,
        "respiratory_rate": 16.0,
        "temperature": 37.0,
        "spo2": 98.0,
        "lactate": 1.0
      }
    }
  ]
}
```

**What to verify:**
- ✅ Risk score < 40
- ✅ Risk level = "normal"
- ✅ No alerts should be created

---

### **Step 5: Seed Warning Vitals** 🟡

**Request:** `POST /seed/warning`

**What it tests:**
- Warning threshold detection (score 40-69)
- Nurse notification triggered
- Alert creation

**Expected Response:**
```json
{
  "seeded": "warning",
  "description": "🟡 Borderline sepsis signals. Nurse notified.",
  "patients_updated": 3,
  "results": [
    {
      "patient_id": 1,
      "patient_name": "John Doe",
      "bed": "ICU-101",
      "risk_score": 52.3,
      "risk_level": "warning",
      "vitals": {
        "heart_rate": 98.0,
        "systolic_bp": 105.0,
        "respiratory_rate": 22.0,
        "temperature": 38.5,
        "spo2": 93.0,
        "lactate": 2.2
      }
    }
  ]
}
```

**What to verify:**
- ✅ Risk score 40-69
- ✅ Risk level = "warning"
- ✅ Alerts should be created (check next step)

---

### **Step 6: View Alerts** 🚨

**Request:** `GET /alerts/`

**What it tests:** Alert listing

**Expected Response:**
```json
[
  {
    "id": 1,
    "patient_id": 1,
    "vital_id": 4,
    "level": "warning",
    "risk_score": 52.3,
    "message": "Sepsis warning: score 52.3. Factors: Elevated heart rate, Low blood pressure, Hypoxemia",
    "triggered_at": "2026-03-21T09:50:00.000Z",
    "resolved": false,
    "nurse_notified": true,
    "nurse_notified_at": "2026-03-21T09:50:00.000Z",
    "doctor_notified": false
  }
]
```

**Additional Tests:**

**Filter Critical Only:** `GET /alerts/?level=critical`

**Filter Warning Only:** `GET /alerts/?level=warning`

**Get Patient Alerts:** `GET /alerts/patient/1`

---

### **Step 7: Seed Critical Vitals** 🔴 ⚡ **MAIN TEST**

**Request:** `POST /seed/critical`

**What it tests:**
- Critical threshold detection (score ≥ 70)
- Nurse + Doctor notification
- **Gemini AI protocol generation** ← KEY FEATURE
- Full multi-agent pipeline

**Expected Response:**
```json
{
  "seeded": "critical",
  "description": "🔴 Critical sepsis signals. Nurse + Doctor notified. Gemini protocol generated.",
  "patients_updated": 3,
  "results": [
    {
      "patient_id": 1,
      "patient_name": "John Doe",
      "bed": "ICU-101",
      "risk_score": 87.5,
      "risk_level": "critical",
      "vitals": {
        "heart_rate": 118.0,
        "systolic_bp": 88.0,
        "respiratory_rate": 28.0,
        "temperature": 39.2,
        "spo2": 88.0,
        "lactate": 4.1
      }
    }
  ]
}
```

**What to verify:**
- ✅ Risk score ≥ 70
- ✅ Risk level = "critical"
- ✅ Alerts created with doctor_notified = true
- ✅ **Gemini protocol should be generated** (check next step)

---

### **Step 8: View Protocols** 📄 ⚡ **GEMINI AI OUTPUT**

**Request:** `GET /protocols/`

**What it tests:** Gemini-generated treatment protocols

**Expected Response:**
```json
[
  {
    "id": 1,
    "patient_id": 1,
    "alert_id": 3,
    "risk_score": 87.5,
    "gemini_recommendation": "**CRITICAL SEPSIS PROTOCOL - Patient: John Doe (45M, ICU-101)**\n\n**Immediate Actions (Hour 1):**\n1. Administer IV fluid bolus: 30 mL/kg crystalloid (Lactated Ringer's)\n2. Obtain blood cultures (2 sets) before antibiotics\n3. Start broad-spectrum antibiotics within 1 hour\n4. Monitor vital signs every 15 minutes\n5. Insert arterial line for continuous BP monitoring\n\n**Antibiotic Recommendation:**\nVancomycin 15-20 mg/kg IV + Piperacillin-Tazobactam 4.5g IV q6h\n*Note: Patient allergic to Penicillin - substitute with Meropenem 1g IV q8h*\n\n**Additional Interventions:**\n- Place central venous catheter for CVP monitoring\n- Target MAP ≥ 65 mmHg\n- Consider vasopressors (Norepinephrine) if hypotension persists\n- Supplemental O2 to maintain SpO2 > 94%\n- Serial lactate measurements every 2-4 hours\n\n**Rationale:**\nPatient shows signs of septic shock with:\n- Tachycardia (HR 118)\n- Hypotension (SBP 88)\n- Hypoxemia (SpO2 88%)\n- Elevated lactate (4.1 mmol/L)\n- Fever (39.2°C)\n- Tachypnea (RR 28)\n\nComorbid diabetes increases infection risk. Early aggressive resuscitation and antibiotics critical for survival.",
    "antibiotic_suggestion": "Vancomycin + Meropenem (Penicillin allergy)",
    "immediate_actions": "IV fluids, Blood cultures, Antibiotics, Continuous monitoring, Arterial line",
    "rationale": "Septic shock with multi-organ dysfunction. Early goal-directed therapy per Surviving Sepsis Campaign guidelines.",
    "status": "pending",
    "generated_at": "2026-03-21T09:52:00.000Z",
    "reviewed_by": null,
    "reviewed_at": null,
    "doctor_notes": null,
    "nurse_notified": false
  }
]
```

**What to verify:**
- ✅ Gemini recommendation is detailed and personalized
- ✅ Considers patient allergies (Penicillin → suggests alternative)
- ✅ Considers patient comorbidities (Diabetes)
- ✅ Includes immediate actions, antibiotics, rationale
- ✅ Status = "pending" (awaiting doctor review)

**Get Pending Protocols Only:** `GET /protocols/pending`

**Get Specific Protocol:** `GET /protocols/1`

**Get Patient Protocols:** `GET /protocols/patient/1`

---

### **Step 9: Approve Protocol** ✅

**Request:** `PATCH /protocols/1/review`

**Body:**
```json
{
  "reviewed_by": "Dr. Sarah Wilson",
  "notes": "Protocol approved. Excellent recommendation considering patient allergies. Proceed with Meropenem + Vancomycin.",
  "action": "approved"
}
```

**What it tests:**
- Doctor review workflow
- Nurse notification after approval
- Status change

**Expected Response:**
```json
{
  "status": "approved",
  "protocol_id": 1,
  "nurse_notified": true,
  "message": "Protocol approved. Nurse has been notified to implement orders."
}
```

**Alternative Actions:**
- `"action": "modified"` - Protocol needs changes
- `"action": "rejected"` - Protocol rejected

---

### **Step 10: Add Manual Vitals** 💓

**Request:** `POST /patients/1/vitals`

**Body:**
```json
{
  "heart_rate": 112.0,
  "systolic_bp": 95.0,
  "respiratory_rate": 24.0,
  "temperature": 38.8,
  "spo2": 91.0,
  "lactate": 3.2
}
```

**What it tests:** Manual vital entry with risk calculation

**Expected Response:**
```json
{
  "vital_id": 10,
  "risk_score": 68.5,
  "qsofa": 2,
  "sofa_partial": 3,
  "risk_level": "warning"
}
```

---

### **Step 11: Get Vitals History** 📊

**Request:** `GET /patients/1/vitals`

**What it tests:** Historical vital signs

**Expected Response:** Array of vitals ordered by most recent

---

### **Step 12: Resolve Alert** ✔️

**Request:** `PATCH /alerts/1/resolve?resolved_by=Nurse%20Amanda`

**Query Params:**
- `resolved_by` = "Nurse Amanda"

**What it tests:** Alert resolution workflow

**Expected Response:**
```json
{
  "resolved": 1,
  "by": "Nurse Amanda"
}
```

---

### **Step 13: Analytics** 📈

**Request:** `GET /analytics/accuracy`

**What it tests:** System performance metrics

**Expected Response:**
```json
{
  "total_predictions": 12,
  "true_positives": 8,
  "false_positives": 1,
  "false_negatives": 0,
  "accuracy": 0.89,
  "precision": 0.89,
  "recall": 1.0,
  "insights": "System showing high sensitivity. Low false negative rate indicates good sepsis detection."
}
```

---

**Request:** `GET /analytics/trend/1`

**What it tests:** Patient risk trend over time

**Expected Response:**
```json
{
  "patient_id": 1,
  "patient_name": "John Doe",
  "trend": [
    {"timestamp": "2026-03-21T09:45:00.000Z", "risk_score": 12.5, "level": "normal"},
    {"timestamp": "2026-03-21T09:50:00.000Z", "risk_score": 52.3, "level": "warning"},
    {"timestamp": "2026-03-21T09:52:00.000Z", "risk_score": 87.5, "level": "critical"}
  ]
}
```

---

## 🎨 Complete Testing Sequence

Run these requests **in order** for the full demo:

```
1. GET /health                      ← Verify server
2. POST /patients/                  ← Create patient 1
3. POST /patients/                  ← Create patient 2 (post-surgical)
4. POST /patients/                  ← Create patient 3 (immunocompromised)
5. GET /patients/                   ← List all patients
6. POST /seed/normal                ← Healthy scenario
7. GET /alerts/                     ← Should be empty
8. POST /seed/warning               ← Borderline scenario
9. GET /alerts/                     ← Should see warning alerts
10. POST /seed/critical             ← **CRITICAL - Triggers Gemini**
11. GET /alerts/?level=critical     ← Critical alerts
12. GET /protocols/pending          ← **See Gemini protocols**
13. GET /protocols/1                ← View full protocol details
14. PATCH /protocols/1/review       ← Doctor approves
15. GET /protocols/1                ← Verify status = approved
16. POST /patients/1/vitals         ← Add manual vitals
17. GET /patients/1/vitals          ← View history
18. GET /analytics/trend/1          ← Risk progression
19. PATCH /alerts/1/resolve         ← Resolve alert
20. GET /analytics/accuracy         ← System stats
```

---

## ✅ Expected Behaviors

### **Risk Scoring System:**
- **0-39** → Normal (No action)
- **40-69** → Warning (Nurse notified)
- **70-100** → Critical (Nurse + Doctor + Gemini protocol)

### **Context Adjustments:**
- **Post-surgical patients:** +5 risk bonus
- **Immunocompromised patients:** +8 risk bonus

### **Gemini Protocol Features:**
- ✅ Personalized to patient (age, gender, diagnosis)
- ✅ Considers allergies (suggests alternatives)
- ✅ Considers comorbidities (diabetes, COPD, etc.)
- ✅ Includes immediate actions (hour 1)
- ✅ Antibiotic recommendations
- ✅ Rationale based on Surviving Sepsis Campaign guidelines

---

## 🐛 Common Issues & Troubleshooting

### **Issue: "GEMINI_API_KEY not found"**
**Solution:** 
- Check `.env` file exists in `backend/` folder
- Verify: `GEMINI_API_KEY=your_actual_key`
- Restart the server

### **Issue: "No module named 'app'"**
**Solution:**
- Ensure you're in `backend/` directory
- Run: `cd E:\Ideathon2026\backend`

### **Issue: Protocol not generated**
**Solution:**
- Risk score must be ≥ 70
- Check if Gemini API key is valid
- Check backend console for errors

### **Issue: Alerts not showing**
**Solution:**
- Risk level must change from previous state
- Run seed endpoints in order: normal → warning → critical

### **Issue: 404 Patient/Protocol not found**
**Solution:**
- Verify ID exists
- Use `GET /patients/` or `GET /protocols/` to list all

---

## 🎯 Success Criteria

You've successfully tested the system if you can:
- ✅ Create patients
- ✅ Trigger warning alerts (score 40-69)
- ✅ Trigger critical alerts (score ≥ 70)
- ✅ **See Gemini-generated protocol with personalized recommendations**
- ✅ Approve protocol as doctor
- ✅ View analytics and trends

---

## 📚 Additional Notes

### **Notification Endpoints:**
Configure these in `.env` for real notifications:
```env
NURSE_WEBHOOK_URL=https://your-webhook-url
DOCTOR_WEBHOOK_URL=https://your-webhook-url
```

### **Database Location:**
- SQLite DB: `E:\Ideathon2026\backend\asclepius.db`
- Reset: Delete the file and run `python -m db.init_db` again

### **API Documentation:**
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

**🎉 Happy Testing! The Gemini protocol generation is the star feature - watch for detailed, personalized sepsis treatment plans!**
