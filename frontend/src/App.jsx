import { useState } from "react";

function Calculator() {
  const [formData, setFormData] = useState({
    transport: {},
    energy: {},
    food: {},
    waste: {}
  });
  const [result, setResult] = useState(null);

  const handleCalculate = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Error calculating footprint:", err);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto text-center">
      <h1 className="text-2xl font-bold">🌍 Carbon Footprint Calculator</h1>
      <button
        onClick={handleCalculate}
        className="mt-4 px-6 py-2 bg-green-600 text-white rounded-xl shadow-md"
      >
        Calculate
      </button>

      {result && (
        <div className="mt-6 bg-gray-100 p-4 rounded-lg">
          <h2 className="font-semibold">Results</h2>
          <p>Total Annual: {result.total_annual.toFixed(2)} kg CO₂</p>
          <pre className="text-left mt-2 text-sm bg-white p-2 rounded">
            {JSON.stringify(result.recommendations, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

export default Calculator;
