"""
Gemini Client — Asclepius AI
Uses Gemini to generate clinical sepsis protocols with RAG context.
"""
import google.generativeai as genai
from config import get_settings

settings = get_settings()

# Surviving Sepsis Campaign knowledge base (RAG context)
SEPSIS_KNOWLEDGE_BASE = """
=== Surviving Sepsis Campaign 2021 Guidelines (Key Excerpts) ===

HOUR-1 BUNDLE (must complete within 1 hour of recognition):
1. Measure lactate. Re-measure if initial >2 mmol/L
2. Obtain blood cultures BEFORE antibiotics
3. Administer broad-spectrum antibiotics
4. Begin 30mL/kg crystalloid for hypotension or lactate ≥4 mmol/L
5. Apply vasopressors if hypotensive during/after fluids (MAP target ≥65 mmHg)

ANTIBIOTIC GUIDANCE:
- Start within 1 hour of sepsis recognition
- Use broad-spectrum covering likely pathogens
- Community-acquired: Piperacillin-Tazobactam 4.5g IV q6h OR Cefepime 2g IV q8h
- Hospital-acquired / VAP risk: Meropenem 1g IV q8h + anti-MRSA (Vancomycin)
- Adjust for: renal function (CrCl), allergies, local antibiogram
- De-escalate once cultures + sensitivities return (48–72h)

PENICILLIN ALLERGY:
- Mild (rash only): Cephalosporins generally safe (5% cross-reactivity)
- Severe (anaphylaxis): Use Aztreonam + Vancomycin or Meropenem (low cross-reactivity)

RENAL DOSING:
- CrCl 30–60: Meropenem 500mg q8h, Vancomycin trough-guided
- CrCl <30: Meropenem 500mg q12h, consult pharmacist

FLUID RESUSCITATION:
- Crystalloid preferred (Normal Saline or Lactated Ringer's)
- Avoid hydroxyethyl starches
- Reassess after each bolus (30 mL/kg target)

VASOPRESSORS:
- First-line: Norepinephrine 0.01–3 mcg/kg/min
- Second-line: Vasopressin 0.03 units/min (if NE >0.25)
- Target MAP ≥65 mmHg

SOURCE CONTROL:
- Identify and control infection source within 6–12 hours
- Consider imaging if source unclear

MONITORING:
- Lactate-guided resuscitation (normalize within 2–4 hours)
- ScvO2 >70% target
- Urine output >0.5 mL/kg/hr
=== End Guidelines ===
"""


def _build_prompt(patient_context: dict, risk_score: float, vitals: dict, factors: list) -> str:
    return f"""
You are a critical care AI assistant for Asclepius AI ICU system.
A patient has triggered a CRITICAL sepsis alert (risk score: {risk_score}/100).

{SEPSIS_KNOWLEDGE_BASE}

=== PATIENT CONTEXT ===
Name: {patient_context.get('name', 'Unknown')}
Age: {patient_context.get('age', 'Unknown')}
Gender: {patient_context.get('gender', 'Unknown')}
Diagnosis: {patient_context.get('diagnosis', 'Unknown')}
Allergies: {patient_context.get('allergies', 'None')}
Comorbidities: {patient_context.get('comorbidities', 'None')}
Post-surgical: {patient_context.get('is_post_surgical', False)}
Immunocompromised: {patient_context.get('is_immunocompromised', False)}

=== CURRENT VITALS (Critical Alert) ===
Heart Rate: {vitals.get('heart_rate')} bpm
Systolic BP: {vitals.get('systolic_bp')} mmHg
Respiratory Rate: {vitals.get('respiratory_rate')} breaths/min
Temperature: {vitals.get('temperature')}°C
SpO2: {vitals.get('spo2')}%
Lactate: {vitals.get('lactate')} mmol/L

Risk Score: {risk_score}/100
Contributing Factors: {', '.join(factors)}

=== YOUR TASK ===
Generate a structured sepsis response protocol. Respond in this EXACT format:

**IMMEDIATE ACTIONS (Next 15 minutes)**
- [action 1]
- [action 2]
...

**ANTIBIOTIC RECOMMENDATION**
Primary: [drug, dose, route, frequency] — [rationale]
[Adjust for allergies/renal function if needed]

**FLUID & VASOPRESSOR PLAN**
- [fluid orders]
- [vasopressor threshold if needed]

**MONITORING TARGETS**
- [monitoring parameters]

**CLINICAL RATIONALE**
[2–3 sentences explaining the reasoning based on this patient's specific context]

**CONTRAINDICATIONS NOTED**
[Any specific contraindications for this patient]

Be specific, practical, and account for the patient's allergies and comorbidities.
"""


async def generate_sepsis_protocol(
    patient_context: dict,
    risk_score: float,
    vitals: dict,
    contributing_factors: list,
) -> dict:
    """Call Gemini and return structured protocol."""
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = _build_prompt(patient_context, risk_score, vitals, contributing_factors)

    try:
        response = model.generate_content(prompt)
        text = response.text

        # Extract sections
        def extract_section(content: str, header: str) -> str:
            lines = content.split("\n")
            collecting = False
            result = []
            for line in lines:
                if header.lower() in line.lower():
                    collecting = True
                    continue
                if collecting:
                    if line.startswith("**") and header.lower() not in line.lower():
                        break
                    result.append(line)
            return "\n".join(result).strip()

        return {
            "full_recommendation": text,
            "immediate_actions": extract_section(text, "IMMEDIATE ACTIONS"),
            "antibiotic_suggestion": extract_section(text, "ANTIBIOTIC RECOMMENDATION"),
            "monitoring": extract_section(text, "MONITORING TARGETS"),
            "rationale": extract_section(text, "CLINICAL RATIONALE"),
            "contraindications": extract_section(text, "CONTRAINDICATIONS"),
        }

    except Exception as e:
        return {
            "full_recommendation": f"Gemini unavailable: {str(e)}. Apply Surviving Sepsis Hour-1 Bundle immediately.",
            "immediate_actions": "1. Blood cultures x2\n2. Broad-spectrum antibiotics\n3. 30mL/kg crystalloid\n4. Measure lactate",
            "antibiotic_suggestion": "Piperacillin-Tazobactam 4.5g IV q6h (check allergies first)",
            "monitoring": "MAP ≥65 mmHg, urine output ≥0.5mL/kg/hr, lactate normalization",
            "rationale": "Fallback protocol applied due to AI unavailability.",
            "contraindications": "Always verify allergies before administering antibiotics.",
        }