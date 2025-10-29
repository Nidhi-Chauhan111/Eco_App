import React, { useState } from "react";
import "./App.css";

function Page2() {
  const [transport, setTransport] = useState(0);
  const [electricity, setElectricity] = useState(0);
  const [food, setFood] = useState(0);
  const [result, setResult] = useState(null);

  const calculateFootprint = () => {
    const total = (transport * 0.3 + electricity * 0.5 + food * 0.2).toFixed(2);
    setResult(total);
  };

  return (
    <div className="calculator-container">
      <div className="calculator-header fade-in">
        <h1>🌿 Calculate Your Daily Impact</h1>
        <p>Estimate your daily carbon footprint and discover where you can improve!</p>
      </div>

      <div className="calculator-grid">
        <div className="calc-card slide-up">
          <h3>🚗 Transport</h3>
          <p>How many kilometers do you travel daily?</p>
          <input
            type="range"
            min="0"
            max="1000"
            value={transport}
            onChange={(e) => setTransport(e.target.value)}
          />
          <span>{transport} km/day</span>
        </div>

        <div className="calc-card slide-up delay-1">
          <h3>💡 Electricity</h3>
          <p>How many kWh do you use daily?</p>
          <input
            type="range"
            min="0"
            max="1000"
            value={electricity}
            onChange={(e) => setElectricity(e.target.value)}
          />
          <span>{electricity} kWh/day</span>
        </div>

        <div className="calc-card slide-up delay-2">
          <h3>🍽️ Food</h3>
          <p>How many meat-based meals do you have per day?</p>
          <input
            type="range"
            min="0"
            max="10"
            value={food}
            onChange={(e) => setFood(e.target.value)}
          />
          <span>{food} meals/day</span>
        </div>
      </div>

      <button className="calc-btn bounce" onClick={calculateFootprint}>
        Calculate 🌎
      </button>

      {result && (
        <div className="result-card pop-in">
          <h2>Your Estimated Carbon Footprint:</h2>
          <h1>{result} kg CO₂/day</h1>
          <p>
            Great job! Every small change helps — try carpooling, using LED lights, or eating more plant-based meals.
          </p>
        </div>
      )}
    </div>
  );
}

export default Page2;
