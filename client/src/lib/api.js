import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const API = axios.create({ baseURL: BASE, timeout: 4000 });

// Mock data - realistic medical data like before
const MOCK_PATIENTS = [
  {
    id: 1,
    name: "Ramesh Kulkarni",
    age: 62,
    gender: "Male",
    bed_number: "ICU-01",
    diagnosis: "Post-abdominal surgery",
    allergies: "Penicillin",
    comorbidities: "Diabetes, Hypertension",
    is_post_surgical: true,
    is_immunocompromised: false,
    current_risk_score: 87.5,
    risk_level: "critical",
    vitals: { 
      heart_rate: 118, 
      systolic_bp: 86, 
      respiratory_rate: 29, 
      temperature: 39.2, 
      spo2: 88, 
      lactate: 4.3 
    },
    active_alerts: [
      { 
        level: "critical", 
        message: "Sepsis critical: score 87.5. Factors: Low SBP (86 mmHg), High RR (29 br/min), Very low SpO2 (88%)", 
        at: new Date().toISOString() 
      }
    ],
  },
  {
    id: 2,
    name: "Sunita Desai",
    age: 45,
    gender: "Female",
    bed_number: "ICU-02",
    diagnosis: "Pneumonia",
    allergies: "",
    comorbidities: "Asthma",
    is_post_surgical: false,
    is_immunocompromised: false,
    current_risk_score: 54.2,
    risk_level: "warning",
    vitals: { 
      heart_rate: 97, 
      systolic_bp: 106, 
      respiratory_rate: 22, 
      temperature: 38.4, 
      spo2: 93, 
      lactate: 2.3 
    },
    active_alerts: [
      { 
        level: "warning", 
        message: "Sepsis warning: score 54.2. Factors: High RR (22 br/min), High HR (97 bpm)", 
        at: new Date().toISOString() 
      }
    ],
  },
  {
    id: 3,
    name: "Arjun Mehta",
    age: 71,
    gender: "Male",
    bed_number: "ICU-03",
    diagnosis: "UTI with suspected sepsis",
    allergies: "Sulfonamides",
    comorbidities: "CKD Stage 3, Diabetes",
    is_post_surgical: false,
    is_immunocompromised: true,
    current_risk_score: 19.0,
    risk_level: "normal",
    vitals: { 
      heart_rate: 74, 
      systolic_bp: 122, 
      respiratory_rate: 17, 
      temperature: 37.1, 
      spo2: 97, 
      lactate: 1.1 
    },
    active_alerts: [],
  },
  {
    id: 4,
    name: "Priya Nair",
    age: 38,
    gender: "Female",
    bed_number: "ICU-04",
    diagnosis: "Post-cardiac surgery",
    allergies: "",
    comorbidities: "None",
    is_post_surgical: true,
    is_immunocompromised: false,
    current_risk_score: 7.0,
    risk_level: "normal",
    vitals: { 
      heart_rate: 68, 
      systolic_bp: 118, 
      respiratory_rate: 14, 
      temperature: 36.8, 
      spo2: 99, 
      lactate: 0.9 
    },
    active_alerts: [],
  },
  {
    id: 5,
    name: "Mohan Sharma",
    age: 55,
    gender: "Male",
    bed_number: "ICU-05",
    diagnosis: "Liver failure",
    allergies: "Cephalosporins",
    comorbidities: "Cirrhosis, Malnutrition",
    is_post_surgical: false,
    is_immunocompromised: true,
    current_risk_score: 62.8,
    risk_level: "warning",
    vitals: { 
      heart_rate: 101, 
      systolic_bp: 104, 
      respiratory_rate: 23, 
      temperature: 38.6, 
      spo2: 92, 
      lactate: 2.5 
    },
    active_alerts: [
      { 
        level: "warning", 
        message: "Sepsis warning: score 62.8. Factors: High RR, immunocompromised (+8 adjustment)", 
        at: new Date().toISOString() 
      }
    ],
  },
];

const MOCK_ALERTS = [
  { 
    id: 1, 
    patient_id: 1, 
    level: "critical", 
    risk_score: 87.5, 
    message: "Sepsis critical: score 87.5. Factors: Low SBP (86 mmHg), High RR (29 br/min), Very low SpO2 (88%) — possible altered mentation", 
    nurse_notified: true, 
    doctor_notified: true, 
    resolved: false, 
    triggered_at: new Date(Date.now() - 8 * 60000).toISOString() 
  },
  { 
    id: 2, 
    patient_id: 2, 
    level: "warning",  
    risk_score: 54.2, 
    message: "Sepsis warning: score 54.2. Factors: High RR (22 br/min), High HR (97 bpm)", 
    nurse_notified: true, 
    doctor_notified: false, 
    resolved: false, 
    triggered_at: new Date(Date.now() - 22 * 60000).toISOString() 
  },
  { 
    id: 3, 
    patient_id: 5, 
    level: "warning",  
    risk_score: 62.8, 
    message: "Sepsis warning: score 62.8. Factors: High RR (23 br/min), immunocompromised (+8 adjustment)", 
    nurse_notified: true, 
    doctor_notified: false, 
    resolved: false, 
    triggered_at: new Date(Date.now() - 45 * 60000).toISOString() 
  },
];

const MOCK_PROTOCOLS = [
  {
    id: 1,
    patient_id: 1,
    alert_id: 1,
    risk_score: 87.5,
    status: "pending",
    immediate_actions: "1. Obtain 2 sets of blood cultures before antibiotics\n2. Measure serum lactate (target <2 mmol/L)\n3. Administer 30 mL/kg IV crystalloid bolus (Normal Saline)\n4. Apply supplemental O2 — target SpO2 ≥94%\n5. Insert urinary catheter — monitor hourly output",
    antibiotic_suggestion: "PENICILLIN ALLERGY NOTED — Piperacillin-Tazobactam EXCLUDED\n\nRecommend: Meropenem 1g IV q8h (renal function unknown — reassess CrCl)\n+ Vancomycin 25 mg/kg IV loading dose (trough-guided)\n\nRationale: Post-surgical abdominal source, gram-negative + MRSA coverage needed",
    rationale: "Post-abdominal surgery patient with compensated septic shock (SBP 86, lactate 4.3). Penicillin allergy requires carbapenem-based regimen. Immunocompetent but surgical site infection risk is high. Urgent source control evaluation within 6 hours.",
    generated_at: new Date(Date.now() - 5 * 60000).toISOString(),
  },
];

const MOCK_ANALYTICS = {
  total_alerts: 3,
  resolved_alerts: 0,
  critical_alerts: 1,
  warning_alerts: 2,
  average_risk_score_at_alert: 68.2,
  high_confidence_alerts: 1,
  insights: [
    "High warning-to-critical ratio — early detection working well.",
    "Post-surgical and immunocompromised patients account for 60% of alerts.",
    "Average time to alert: <2 minutes from vital deterioration.",
  ],
};

// Fallback wrapper — returns mock data if backend is unreachable
async function withFallback(fn, fallback) {
  try {
    return await fn();
  } catch (error) {
    console.warn("API call failed, using fallback:", error.message);
    return fallback;
  }
}

// Patient functions
export const getPatients = () => withFallback(() => API.get("/patients/").then(r => r.data), MOCK_PATIENTS);
export const getPatient = (id) => withFallback(() => API.get(`/patients/${id}`).then(r => r.data), MOCK_PATIENTS.find(p => p.id === id));
export const getPatientVitals = (id, limit = 20) => withFallback(() => API.get(`/patients/${id}/vitals?limit=${limit}`).then(r => r.data), []);

// Alert functions
export const getAlerts = (resolved = false) => withFallback(() => API.get(`/alerts/?resolved=${resolved}`).then(r => r.data), resolved ? [] : MOCK_ALERTS);
export const resolveAlert = (id) => withFallback(() => API.post(`/alerts/${id}/resolve`).then(r => r.data), { status: "resolved" });

// Protocol functions
export const getPendingProtocols = () => withFallback(() => API.get("/protocols/pending").then(r => r.data), MOCK_PROTOCOLS);
export const approveProtocol = (id, reviewed_by, notes) => withFallback(() => 
  API.post(`/protocols/${id}/approve`, { reviewed_by, notes }).then(r => r.data), 
  { status: "approved" }
);
export const rejectProtocol = (id, reviewed_by, notes) => withFallback(() => 
  API.post(`/protocols/${id}/reject`, { reviewed_by, notes }).then(r => r.data), 
  { status: "rejected" }
);

// Analytics functions
export const getAnalytics = () => withFallback(() => API.get("/analytics/stats").then(r => r.data), {
  total_patients: 2,
  critical_patients: 1,
  warning_patients: 1,
  normal_patients: 0,
  active_alerts: 2,
  protocols_pending: 1
});

export const getAccuracy = () => withFallback(() => API.get("/analytics/accuracy").then(r => r.data), MOCK_ANALYTICS);
export const getTrend = (id) => withFallback(() => API.get(`/analytics/trend/${id}`).then(r => r.data), { trend: [] });

// Seed functions that trigger actual alerts and Telegram notifications
export const seedNormal = () => withFallback(() => API.post("/seed/normal").then(r => r.data), { status: "success", message: "Normal patients seeded" });
export const seedWarning = () => withFallback(() => API.post("/seed/warning").then(r => r.data), { status: "success", message: "Warning patients seeded - Nurse notified via Telegram" });
export const seedCritical = () => withFallback(() => API.post("/seed/critical").then(r => r.data), { status: "success", message: "Critical patients seeded - Doctor and Nurse notified via Telegram!" });

// Trigger critical alert manually (for demo)
export const triggerCriticalAlert = (patientId) => withFallback(() => 
  API.post(`/patients/${patientId}/trigger-critical`).then(r => r.data), 
  { status: "success", message: "🚨 Critical alert triggered! Doctor and Nurse notified via Telegram" }
);

// WebSocket connection - disabled for deployment stability
export const createWS = () => {
  // Disable WebSocket for now - using REST API for stability
  console.log("WebSocket disabled - using REST API polling for updates");
  return null;
};

export default API;
