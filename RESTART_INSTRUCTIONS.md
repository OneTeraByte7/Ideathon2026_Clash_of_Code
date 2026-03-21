## 🔄 Complete Server Restart Instructions

### Step 1: Stop the Server
1. Go to the terminal where uvicorn is running
2. Press **Ctrl+C** to stop it
3. Wait until you see "Shutting down" message

### Step 2: Verify the Code Change
Run this command to verify the model name:
```bash
cd E:\Ideathon2026\backend
grep -n "GenerativeModel" core/gemini_client.py
```

You should see:
```
model = genai.GenerativeModel("gemini-2.5-flash")
```

### Step 3: Clear Old Protocols (Optional)
To start with fresh data:
```bash
cd E:\Ideathon2026\backend
del asclepius.db
python -m db.init_db
```

### Step 4: Restart the Server
```bash
uvicorn main:app --reload --port 8000
```

### Step 5: Test in Thunder Client

1. **Create a NEW patient** (POST /patients/)
   ```json
   {
     "name": "Jane Smith",
     "age": 62,
     "gender": "Female",
     "bed_number": "ICU-102",
     "diagnosis": "Post-surgical infection",
     "allergies": "Penicillin",
     "comorbidities": "Hypertension, COPD",
     "is_post_surgical": true,
     "is_immunocompromised": false
   }
   ```

2. **Trigger Critical Alert** (POST /seed/critical)

3. **Check Protocols** (GET /protocols/)
   - Should now show full Gemini 2.5 Flash response
   - Should have personalized recommendations
   - Should consider Penicillin allergy
   - Should reference COPD and post-surgical status

### ✅ Success Indicators:
- `gemini_recommendation` is long and detailed (not "Gemini unavailable")
- `antibiotic_suggestion` mentions alternatives to Penicillin
- `rationale` references the patient's specific conditions
- No "404" error messages

### 🐛 If Still Not Working:
1. Check the server logs for errors
2. Verify the file was saved (open gemini_client.py and check line 124)
3. Make sure you stopped the OLD server before starting new one
