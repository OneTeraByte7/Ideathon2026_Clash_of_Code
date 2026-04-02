import { useEffect, useState } from "react";


export default function HealthTipWidget() {
  const [tip, setTip] = useState("");

  useEffect(() => {
    const baseUrl = import.meta.env.VITE_API_URL;
    fetch(`${baseUrl}/health-tip`)
      .then(res => res.json())
      .then(data => setTip(data.tip))
      .catch(() => setTip("Failed to fetch health tip"));
  }, []);

  return (
    <div className="bg-blue-50 border border-blue-200 rounded p-4 my-4 shadow-sm">
      <h3 className="font-semibold text-blue-700 mb-2">💡 Health Tip</h3>
      <span className="text-blue-900">{tip}</span>
    </div>
  );
}
