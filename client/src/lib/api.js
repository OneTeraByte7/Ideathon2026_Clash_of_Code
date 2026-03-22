import axios from "axios";
import { MOCK_PATIENTS, MOCK_ALERTS, MOCK_PROTOCOLS, MOCK_ANALYTICS } from "./mockData";

const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const API = axios.create({ baseURL: BASE, timeout: 4000 });

// Fallback wrapper — returns mock data if backend is unreachable
async function withFallback(fn, fallback) {
  try { return await fn(); }
  catch { return fallback; }
}

export const getPatients    = () => withFallback(() => API.get("/patients/").then(r => r.data), MOCK_PATIENTS);
export const getAlerts      = (resolved = false) => withFallback(() => API.get(`/alerts/?resolved=${resolved}`).then(r => r.data), resolved ? [] : MOCK_ALERTS);
export const getPatientVitals = (id, limit = 20) => withFallback(() => API.get(`/patients/${id}/vitals?limit=${limit}`).then(r => r.data), []);
export const getPendingProtocols = () => withFallback(() => API.get("/protocols/pending").then(r => r.data), MOCK_PROTOCOLS);
export const getAccuracy    = () => withFallback(() => API.get("/analytics/accuracy").then(r => r.data), MOCK_ANALYTICS);
export const getTrend       = (id) => withFallback(() => API.get(`/analytics/trend/${id}`).then(r => r.data), { trend: [] });

export const seedNormal   = () => API.post("/seed/normal").then(r => r.data);
export const seedWarning  = () => API.post("/seed/warning").then(r => r.data);
export const seedCritical = () => API.post("/seed/critical").then(r => r.data);

export const approveProtocol = (id, reviewed_by, notes) =>
  API.patch(`/protocols/${id}/review`, { reviewed_by, notes, action: "approved" }).then(r => r.data);

export const resolveAlert = (id) =>
  API.patch(`/alerts/${id}/resolve?resolved_by=doctor`).then(r => r.data);

export const triggerCriticalAlert = (patientId) =>
  API.post(`/patients/${patientId}/trigger-critical`).then(r => r.data);

export const createWS = () => {
  const wsUrl = BASE.replace(/^http/, "ws") + "/ws/icu";
  console.log("Connecting to WebSocket:", wsUrl);
  try {
    return new WebSocket(wsUrl);
  } catch (error) {
    console.error("Failed to create WebSocket:", error);
    return null;
  }
};

export default API;