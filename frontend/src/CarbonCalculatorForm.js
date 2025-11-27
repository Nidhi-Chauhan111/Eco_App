import React, { useState } from 'react';

export default function CarbonCalculatorForm({ onCalculate }) {
  const [travel, setTravel] = useState('0');
  const [carKm, setCarKm] = useState('0');
  const [energy, setEnergy] = useState('0');
  const [food, setFood] = useState('average');

  const handleSubmit = e => {
    e.preventDefault();
    const flightFactor = 0.115;
    const carFactor = 0.00021;
    const energyFactor = 0.000475;
    const foodFactors = {
      average: 2.5,
      vegetarian: 1.7,
      vegan: 1.5,
      highMeat: 3.3,
    };

    const flightCO2 = parseFloat(travel) * flightFactor;
    const carCO2 = parseFloat(carKm) * 52 * carFactor;
    const energyCO2 = parseFloat(energy) * 12 * energyFactor;
    const foodCO2 = foodFactors[food];

    const totalCO2 = flightCO2 + carCO2 + energyCO2 + foodCO2;
    onCalculate(totalCO2);
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 400, margin: 'auto' }}>
      <h2>Carbon Footprint Calculator</h2>
      <label>
        Flights per year:
        <input type="text" min="0" value={travel} onChange={e => setTravel(e.target.value)} />
      </label>
      <label>
        Car km per week:
        <input type="text" min="0" value={carKm} onChange={e => setCarKm(e.target.value)} />
      </label>
      <label>
        Monthly electricity usage (kWh):
        <input type="text" min="0" value={energy} onChange={e => setEnergy(e.target.value)} />
      </label>
      <label>
        Diet type:
        <select value={food} onChange={e => setFood(e.target.value)}>
          <option value="average">Average</option>
          <option value="vegetarian">Vegetarian</option>
          <option value="vegan">Vegan</option>
          <option value="highMeat">High Meat</option>
        </select>
      </label>
      <button type="submit" style={{ marginTop: 10 }}>Calculate</button>
    </form>
  );
}
