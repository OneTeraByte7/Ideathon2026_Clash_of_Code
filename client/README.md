# Asclepius AI — Frontend Client

Dark biopunk ICU dashboard with real-time sepsis monitoring.

## Stack
- React 18 + Vite · Framer Motion · Recharts · Tailwind CSS v3 · React Router v6

## Install & Run

```bash
cd asclepius-ai/client
npm install
npm run dev
# → http://localhost:5173
```

## Requires backend running
```bash
# Separate terminal, from asclepius-ai/
uvicorn app.main:app --reload --port 8000
```

## Pages
| Route         | Page             |
|--------------|-----------------|
| /             | ICU Grid         |
| /alerts       | Alert Center     |
| /protocols    | Protocol Review  |
| /analytics    | Analytics        |
