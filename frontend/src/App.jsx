import { useState } from "react";
import "./App.css";
import Sidebar from "./Sidebar";
import Journal from "./pages/Journal"; // create this file
function App() {
  const [formData, setFormData] = useState({
    transport: {},
    energy: {},
    food: {},
    waste: {}
  });
  const [result, setResult] = useState(null);
<Route path="/journal" element={<Journal />} />
  const handleCalculate = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Error calculating footprint:", err);
    }
  };

  return (
    <div className="calculator-container">
      <div className="calculator-header">
        <h1>🌍 Carbon Footprint Calculator</h1>
      </div>
      <button onClick={handleCalculate} className="calc-btn">
        Calculate
      </button>

      {result && (
        <div className="result-card">
          <h2>Results</h2>
          <p><b>Total Annual:</b> {result.total_annual.toFixed(2)} kg CO₂</p>
          <pre>{JSON.stringify(result.recommendations, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;  