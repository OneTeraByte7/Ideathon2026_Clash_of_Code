import { useEffect, useState } from "react";

export default function HealthTipWidget() {
  const [tip, setTip] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/health-tip")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch health tip");
        return res.json();
      })
      .then((data) => {
        setTip(data.tip);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-blue-50 border border-blue-200 rounded p-4 my-4 shadow-sm">
      <h3 className="font-semibold text-blue-700 mb-2">💡 Health Tip</h3>
      {loading && <span>Loading...</span>}
      {error && <span className="text-red-500">{error}</span>}
      {!loading && !error && <span className="text-blue-900">{tip}</span>}
    </div>
  );
}
