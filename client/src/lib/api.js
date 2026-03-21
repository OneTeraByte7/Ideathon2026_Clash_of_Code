import axios from "axios";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const API = axios.create({ baseURL: BASE, timeout: 4000 });

// Mock data - inline to avoid import issues
const MOCK_PATIENTS = [
  {
    id: "pat_001",
    name: "John Smith",
    age: 65,
    gender: "Male",
    bed_number: "ICU-A01",
    diagnosis: "Post-operative monitoring",
    risk_level: "warning",
    current_risk_score: 45.2,
    vitals: {
      heart_rate: 95,
      systolic_bp: 105,
      respiratory_rate: 22,
      temperature: 38.1,
      spo2: 94,
      lactate: 2.1
    },
    active_alerts: 1
  },
  {
    id: "pat_002", 
    name: "Maria Rodriguez",
    age: 58,
    gender: "Female", 
    bed_number: "ICU-A02",
    diagnosis: "Sepsis monitoring",
    risk_level: "critical",
    current_risk_score: 78.5,
    vitals: {
      heart_rate: 110,
      systolic_bp: 85,
      respiratory_rate: 28,
      temperature: 39.2,
      spo2: 88,
      lactate: 3.8
    },
    active_alerts: 2
  }
];

const MOCK_ALERTS = [
  {
    id: "alert_001",
    patient_id: "pat_002",
    level: "critical",
    message: "Sepsis critical: score 78.5. Factors: High lactate (3.8), Low BP (85), High RR (28)",
    triggered_at: "2024-01-01T12:00:00Z",
    resolved: false
  },
  {
    id: "alert_002",
    patient_id: "pat_001", 
    level: "warning",
    message: "Sepsis warning: score 45.2. Factors: High RR (22), Fever (38.1°C)",
    triggered_at: "2024-01-01T12:30:00Z",
    resolved: false
  }
];

const MOCK_PROTOCOLS = [
  {
    id: "prot_001",
    patient_id: "pat_002",
    status: "pending",
    risk_score: 78.5,
    gemini_recommendation: "Immediate sepsis protocol: Start broad-spectrum antibiotics, fluid resuscitation",
    antibiotic_suggestion: "Piperacillin-tazobactam 4.5g IV q6h",
    immediate_actions: ["Blood cultures", "Lactate level", "IV access", "Fluid bolus"],
    created_at: "2024-01-01T12:00:00Z"
  }
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

// Seed functions
export const seedNormal = () => withFallback(() => API.post("/seed/normal").then(r => r.data), { status: "success", message: "Normal patients seeded" });
export const seedWarning = () => withFallback(() => API.post("/seed/warning").then(r => r.data), { status: "success", message: "Warning patients seeded" });
export const seedCritical = () => withFallback(() => API.post("/seed/critical").then(r => r.data), { status: "success", message: "Critical patients seeded" });

// WebSocket connection
export const createWS = () => {
  try {
    const wsUrl = BASE.replace(/^http/, 'ws') + '/ws';
    return new WebSocket(wsUrl);
  } catch (error) {
    console.warn("WebSocket connection failed:", error);
    return null;
  }
};

export default API;
