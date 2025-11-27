// src/CalculatorComponent.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; 

/*
  Styled Calculator (guided) — purely visual changes:
  - centered section title, quote, bold labels
  - no "Step X of 4" text
  - number inputs allow long values (text + inputMode) and display them fully
  - uses paper-select and paper-input classes from app.css
  - SectionCard variants and badgeEmoji added for nicer look
*/

export default function CalculatorComponent({ apiUrl = "/calculator/calculate", saveToLocal = true }) {
  // --- states for each category ---
  const [transport, setTransport] = useState({
    car_owner: false,
    car_type: "Car (Petrol)",
    car_km_per_week: "",
    bus_km_per_week: "",
    train_km_per_week: "",
    flights_domestic_per_year: "",
    flights_international_per_year: "",
  });

  const [energy, setEnergy] = useState({
    electricity_kwh_per_month: "",
    grid_type: "Electricity (US Grid Average)",
    natural_gas_scf_per_month: "",
    use_natural_gas: false,
    lpg_gallons_per_month: "",
    use_lpg: false,
  });

  const [food, setFood] = useState({
    meat: { beef: "", chicken: "", pork: "", fish: "" },
    dairy: { milk: "", cheese: "" },
    plants: { vegetables: "", fruits: "", grains: "" },
  });

  const [waste, setWaste] = useState({
    levels: { plastic: "none", paper: "none", glass: "none", metal: "none", organic: "medium" },
    recycling: { plastic: "no", paper: "yes", glass: "no", metal: "yes" },
    compost: "no",
  });

  const [step, setStep] = useState(0); // 0..3 input steps, 4 results
  const steps = ["Transportation", "Energy", "Food", "Waste"];
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const navigate = useNavigate();

  // --- updaters (store strings so long numbers display without formatting) ---
  const updateTransport = (k, v) => setTransport((t) => ({ ...t, [k]: v }));
  const updateEnergy = (k, v) => setEnergy((e) => ({ ...e, [k]: v }));
  const updateFood = (group, k, v) => setFood((f) => ({ ...f, [group]: { ...f[group], [k]: v } }));
  const updateWasteLevel = (type, value) => setWaste((w) => ({ ...w, levels: { ...w.levels, [type]: value } }));
  const updateWasteRecycle = (type, value) => setWaste((w) => ({ ...w, recycling: { ...w.recycling, [type]: value } }));

  // build payload converting numeric strings to numbers (backend expects numbers)
  function toNum(s) {
    const n = Number(s);
    return Number.isFinite(n) ? n : 0;
  }

  function buildPayload() {
    const payload = { transportation: {}, energy: {}, food: {}, waste: {} };

    if (transport.car_owner) {
      payload.transportation.car = { type: transport.car_type, km_per_week: toNum(transport.car_km_per_week) };
    }
    if (transport.bus_km_per_week) payload.transportation.bus = { km_per_week: toNum(transport.bus_km_per_week) };
    if (transport.train_km_per_week) payload.transportation.train = { km_per_week: toNum(transport.train_km_per_week) };
    if (transport.flights_domestic_per_year || transport.flights_international_per_year) {
      payload.transportation.flights = {
        domestic_per_year: parseInt(transport.flights_domestic_per_year || "0", 10),
        international_per_year: parseInt(transport.flights_international_per_year || "0", 10),
      };
    }

    payload.energy.electricity = { kwh_per_month: toNum(energy.electricity_kwh_per_month), grid_type: energy.grid_type };
    if (energy.use_natural_gas) payload.energy.natural_gas = { scf_per_month: toNum(energy.natural_gas_scf_per_month) };
    if (energy.use_lpg) payload.energy.lpg = { gallons_per_month: toNum(energy.lpg_gallons_per_month) };

    payload.food.meat = {
      beef: toNum(food.meat.beef),
      chicken: toNum(food.meat.chicken),
      pork: toNum(food.meat.pork),
      fish: toNum(food.meat.fish),
    };
    payload.food.dairy = { milk: toNum(food.dairy.milk), cheese: toNum(food.dairy.cheese) };
    payload.food.plants = {
      vegetables: toNum(food.plants.vegetables),
      fruits: toNum(food.plants.fruits),
      grains: toNum(food.plants.grains),
    };

    payload.waste = { levels: { ...waste.levels }, recycling: { ...waste.recycling }, compost: waste.compost };

    return payload;
  }

  function getAuthToken() {
    return localStorage.getItem("access_token") || localStorage.getItem("token") || null;
  }

  // Place this inside your CalculatorComponent function, before the `return(...)`
  // -------------------------------------------------------------------------
  // Helper: local calculation fallback (mirrors backend)
  function localCalculate(payload) {
    const transportFactors = {
      "Car (Petrol)": 0.23, "Car (Diesel)": 0.25, "Electric Car (EV)": 0.04, "Hybrid Car": 0.12,
      "Public Bus": 0.09, "Train (Regular)": 0.03,
      "Flight (Domestic)": 0.13, "Flight (International)": 0.10
    };
    const energyFactors = {
      "Electricity (US Grid Average)": 0.45, "Electricity (Coal-heavy)": 0.9,
      "Electricity (Natural Gas)": 0.5, "Electricity (Renewable)": 0.05,
      "Natural Gas": 0.0544, "Propane (LPG)": 5.72
    };
    const foodFactors = {
      "Beef (Red Meat)": 27.0, "Chicken": 6.9, "Pork": 7.2, "Fish (Wild-caught)": 2.9,
      "Milk (Dairy)": 3.3, "Cheese (Hard)": 13.5, "Vegetables (Root)": 0.4, "Bananas": 0.7, "Rice": 2.7
    };
    const wasteDefaults = {
      "Plastic_mixed": 3.0, "Plastic_recycled": 2.1, "Paper_mixed": 1.0, "Paper_recycled": 0.5,
      "Glass_mixed": 0.85, "Glass_recycled": 0.64, "Metal_mixed": 2.0, "Metal_recycled": 1.5,
      "Organic_landfill": 0.5, "Organic_compost": 0.1
    };
    const bins = {
      plastic: { none: 0.0, low: 0.12, medium: 0.4, high: 0.8 },
      paper:   { none: 0.0, low: 0.5,  medium: 1.5, high: 3.0 },
      glass:   { none: 0.0, low: 0.3,  medium: 0.8, high: 1.5 },
      metal:   { none: 0.0, low: 0.2,  medium: 0.6, high: 1.2 },
      organic: { none: 0.0, low: 2.0,  medium: 4.0, high: 7.0 }
    };

    // compute transport weekly
    let transportWeekly = 0;
    const t = payload.transportation || {};
    if (t.car) transportWeekly += (t.car.km_per_week || 0) * (transportFactors[t.car.type] || 0.23);
    if (t.bus) transportWeekly += (t.bus.km_per_week || 0) * transportFactors["Public Bus"];
    if (t.train) transportWeekly += (t.train.km_per_week || 0) * transportFactors["Train (Regular)"];
    if (t.flights) {
      const domestic_km_y = (t.flights.domestic_per_year || 0) * 1000;
      const international_km_y = (t.flights.international_per_year || 0) * 8000;
      const annualFlight = (domestic_km_y * transportFactors["Flight (Domestic)"]) + (international_km_y * transportFactors["Flight (International)"]);
      transportWeekly += annualFlight / 52;
    }

    // energy monthly -> weekly conversion same as backend (monthly * 12/52)
    let energyMonthly = 0;
    const e = payload.energy || {};
    if (e.electricity) {
      const gf = energyFactors[e.electricity.grid_type] || energyFactors["Electricity (US Grid Average)"];
      energyMonthly += (e.electricity.kwh_per_month || 0) * gf;
    }
    if (e.natural_gas) energyMonthly += (e.natural_gas.scf_per_month || 0) * energyFactors["Natural Gas"];
    if (e.lpg) energyMonthly += (e.lpg.gallons_per_month || 0) * energyFactors["Propane (LPG)"];
    const energyWeekly = energyMonthly * (12 / 52);

    // food weekly
    let foodWeekly = 0;
    const f = payload.food || {};
    if (f.meat) {
      foodWeekly += (f.meat.beef || 0) * foodFactors["Beef (Red Meat)"];
      foodWeekly += (f.meat.chicken || 0) * foodFactors["Chicken"];
      foodWeekly += (f.meat.pork || 0) * foodFactors["Pork"];
      foodWeekly += (f.meat.fish || 0) * foodFactors["Fish (Wild-caught)"];
    }
    if (f.dairy) {
      foodWeekly += (f.dairy.milk || 0) * foodFactors["Milk (Dairy)"];
      foodWeekly += (f.dairy.cheese || 0) * foodFactors["Cheese (Hard)"];
    }
    if (f.plants) {
      foodWeekly += (f.plants.vegetables || 0) * foodFactors["Vegetables (Root)"];
      foodWeekly += (f.plants.fruits || 0) * foodFactors["Bananas"];
      foodWeekly += (f.plants.grains || 0) * foodFactors["Rice"];
    }

    // waste weekly
    let wasteWeekly = 0;
    const w = payload.waste || {};
    const levels = w.levels || {}; const rec = w.recycling || {}; const compost = (w.compost === "yes");
    wasteWeekly += bins.plastic[levels.plastic || "none"] * (rec.plastic === "yes" ? wasteDefaults.Plastic_recycled : wasteDefaults.Plastic_mixed);
    wasteWeekly += bins.paper[levels.paper || "none"] * (rec.paper === "yes" ? wasteDefaults.Paper_recycled : wasteDefaults.Paper_mixed);
    wasteWeekly += bins.glass[levels.glass || "none"] * (rec.glass === "yes" ? wasteDefaults.Glass_recycled : wasteDefaults.Glass_mixed);
    wasteWeekly += bins.metal[levels.metal || "none"] * (rec.metal === "yes" ? wasteDefaults.Metal_recycled : wasteDefaults.Metal_mixed);
    wasteWeekly += bins.organic[levels.organic || "none"] * (compost ? wasteDefaults.Organic_compost : wasteDefaults.Organic_landfill);

    const results = {
      transportation: { weekly_kg_co2: transportWeekly, annual_kg_co2: transportWeekly * 52 },
      energy: { weekly_kg_co2: energyWeekly, annual_kg_co2: energyWeekly * 52 },
      food: { weekly_kg_co2: foodWeekly, annual_kg_co2: foodWeekly * 52 },
      waste: { weekly_kg_co2: wasteWeekly, annual_kg_co2: wasteWeekly * 52 }
    };
    const totalWeekly = transportWeekly + energyWeekly + foodWeekly + wasteWeekly;
    const totalAnnual = totalWeekly * 52;
    results.summary = { total_weekly_kg_co2: Math.round(totalWeekly * 100) / 100, total_annual_kg_co2: Math.round(totalAnnual * 10) / 10,
      highest_category: ["transportation","energy","food","waste"].reduce((acc, k) => {
        const vals = { transportation: results.transportation.weekly_kg_co2, energy: results.energy.weekly_kg_co2, food: results.food.weekly_kg_co2, waste: results.waste.weekly_kg_co2 };
        return Object.keys(vals).reduce((a,b)=> vals[b] > vals[a] ? b : a, "transportation");
      }, "transportation")
    };
    return results;
  }

  // Unified calculate handler: tries API POST then falls back to localCalculate
  async function handleCalculate(e) {
  e && e.preventDefault();
  setLoading(true);
  setError(null);
  setResults(null);

  const payload = buildPayload(); // your existing function
  const token = getAuthToken();

  // helper to normalize backend response -> the component expects a results-like object
  function applyResults(respData) {
    if (!respData) return;
    // backend may return { message, summary, results } or directly results/summary
    let normalized = null;
    if (respData.results) {
      normalized = respData.results;
    } else if (respData.summary && (respData.transportation || respData.energy)) {
      // looks like full results object
      normalized = respData;
    } else {
      normalized = respData; // best-effort fallback
    }
    setResults(normalized);
    if (saveToLocal) localStorage.setItem("last_calc", JSON.stringify(normalized));
  }
  

  try {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(apiUrl, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      // server returned an error (auth expired / validation / server error)
      console.warn("Server returned non-OK status:", res.status);
      // try to read server error to show to user
      try {
        const errJson = await res.json().catch(() => null);
        if (errJson && errJson.detail) setError(`Server: ${errJson.detail}`);
      } catch (err) {
        // ignore parse errors
      }
      // fallback to local calculation so UX isn't blocked
      const local = localCalculate(payload);
      setResults(local);
      setStep(4);
      if (saveToLocal) localStorage.setItem("last_calc", JSON.stringify(local));
      return;
    }

    // parse server JSON
    const json = await res.json().catch(() => null);
    if (!json) {
      // non-JSON response -> fallback to local
      const local = localCalculate(payload);
      setResults(local);
      setStep(4);
      if (saveToLocal) localStorage.setItem("last_calc", JSON.stringify(local));
      return;


    }

    // success: use API response
    applyResults(json);
    setStep(4);
  } catch (err) {
    // network or unexpected error -> local fallback
    console.warn("Fetch failed, using local fallback:", err);
    try {
      const local = localCalculate(payload);
      setResults(local);
      setStep(4);
      if (saveToLocal) localStorage.setItem("last_calc", JSON.stringify(local));
    } catch (ex) {
      setError("Calculation failed: " + (ex.message || ex));
    }
  } finally {
    setLoading(false);
  }
}


  // navigation
  function goNext() {
    setError(null);
    // minimal validation kept (you asked not to require changes)
    if (step < 3) setStep((s) => s + 1);
  }
  function goBack() {
    setError(null);
    if (step > 0 && step <= 3) setStep((s) => s - 1);
    else if (step === 4) setStep(3);
  }

  // Small UI parts
  function SectionCard({ title, quote, children, variant = "" , badgeEmoji = "🌿" }) {
  // choose floating emoji based on variant (unique for each card)
  const floatingMap = {
    transport: "🚗",
    energy: "⚡",
    food: "🥗",
    waste: "♻️"
  };
  const floating = floatingMap[variant] || "🍃";

  const variantClass = variant ? `variant-${variant}` : "";
  return (
    <div className={`paper-card ${variantClass}`} style={{ position: "relative" }}>
      <div className="card-badge">{badgeEmoji} <span style={{marginLeft:8, fontWeight:700}}>{title}</span></div>

      {/* floating emoji at the top-right */}
      <div className="floating-emoji" aria-hidden>{floating}</div>

      {/* centered title (kept for accessibility) */}
      <div style={{ textAlign: "center", marginTop: 12 }}>
        <div className="section-title" aria-hidden style={{ fontWeight: 700, fontSize: 20 }}>{title}</div>
        {quote && <div className="card-quote" style={{ color: "#6b6b6b", marginTop: 6 }}>{quote}</div>}
      </div>

      <div style={{ marginTop: 6 }}>{children}</div>

      <div className="card-emoji-row" aria-hidden>
        {variant === "transport" && <>🚗 🚌 🚲 🌿</>}
        {variant === "energy" && <>💡 🔋 ☀️ ⚡</>}
        {variant === "food" && <>🥗 🍅 🥛 🌾</>}
        {variant === "waste" && <>♻️ 🗑️ 🍂 🌍</>}
        {!variant && <>🌿 🌱 🌸</>}
      </div>
    </div>
  );
}


  // Steps (contents unchanged aside from classes and variant/badge)
  function TransportStep() {
    return (
      <SectionCard title="TransitFlow" quote="Short trips today, greener tomorrow." variant="transport" badgeEmoji="🚗">
        <div>
          <div className="control-row">
            <div className="label">Do you own/use a car?</div>
            <div className="control"><select className="paper-select" value={transport.car_owner ? "yes" : "no"} onChange={(e) => updateTransport("car_owner", e.target.value === "yes")}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          {transport.car_owner && (
            <>
              <div className="control-row">
                <div className="label">Car type</div>
                <div className="control">
                  <select className="paper-select" value={transport.car_type} onChange={(e) => updateTransport("car_type", e.target.value)}>
                    <option>Car (Petrol)</option>
                    <option>Car (Diesel)</option>
                    <option>Electric Car (EV)</option>
                    <option>Hybrid Car</option>
                  </select>
                </div>
              </div>

              <div className="control-row">
                <div className="label">How many km do you drive per week?</div>
                <div className="control">
                  <input
                    className="paper-input"
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    value={transport.car_km_per_week}
                    onChange={(e) => updateTransport("car_km_per_week", e.target.value)}
                    placeholder="e.g. 150"
                  />
                </div>
              </div>
            </>
          )}

          <div className="control-row">
            <div className="label">Do you use buses?</div>
            <div className="control"><select className="paper-select" value={transport.bus_km_per_week ? "yes" : "no"} onChange={(e) => updateTransport("bus_km_per_week", e.target.value === "yes" ? "" : "")}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Bus - km per week</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={transport.bus_km_per_week} onChange={(e) => updateTransport("bus_km_per_week", e.target.value)} placeholder="e.g. 40" /></div>
          </div>

          <div className="control-row">
            <div className="label">Train - km per week</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={transport.train_km_per_week} onChange={(e) => updateTransport("train_km_per_week", e.target.value)} placeholder="e.g. 20" /></div>
          </div>

          <div className="control-row">
            <div className="label">Flights (domestic / year)</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={transport.flights_domestic_per_year} onChange={(e) => updateTransport("flights_domestic_per_year", e.target.value)} placeholder="0" /></div>
          </div>

          <div className="control-row">
            <div className="label">Flights (international / year)</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={transport.flights_international_per_year} onChange={(e) => updateTransport("flights_international_per_year", e.target.value)} placeholder="0" /></div>
          </div>

        </div>
      </SectionCard>
    );
  }

  function EnergyStep() {
    return (
      <SectionCard title="HomeFlux" quote="Small changes in the home ripple out to the planet." variant="energy" badgeEmoji="⚡">
        <div>
          <div className="control-row">
            <div className="label">Monthly electricity usage (kWh)</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={energy.electricity_kwh_per_month} onChange={(e) => updateEnergy("electricity_kwh_per_month", e.target.value)} placeholder="e.g. 350" /></div>
          </div>

          <div className="control-row">
            <div className="label">Grid type</div>
            <div className="control">
              <select className="paper-select" value={energy.grid_type} onChange={(e) => updateEnergy("grid_type", e.target.value)}>
                <option>Electricity (US Grid Average)</option>
                <option>Electricity (Coal-heavy)</option>
                <option>Electricity (Natural Gas)</option>
                <option>Electricity (Renewable)</option>
              </select>
            </div>
          </div>

          <div className="control-row">
            <div className="label">Do you use natural gas?</div>
            <div className="control"><select className="paper-select" value={energy.use_natural_gas ? "yes" : "no"} onChange={(e) => updateEnergy("use_natural_gas", e.target.value === "yes")}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          {energy.use_natural_gas && <div className="control-row">
            <div className="label">Natural gas (scf / month)</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={energy.natural_gas_scf_per_month} onChange={(e) => updateEnergy("natural_gas_scf_per_month", e.target.value)} placeholder="e.g. 20" /></div>
          </div>}

          <div className="control-row">
            <div className="label">Do you use LPG/Propane?</div>
            <div className="control"><select className="paper-select" value={energy.use_lpg ? "yes" : "no"} onChange={(e) => updateEnergy("use_lpg", e.target.value === "yes")}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          {energy.use_lpg && <div className="control-row">
            <div className="label">LPG (gallons / month)</div>
            <div className="control"><input className="paper-input" type="text" inputMode="numeric" pattern="[0-9]*" value={energy.lpg_gallons_per_month} onChange={(e) => updateEnergy("lpg_gallons_per_month", e.target.value)} placeholder="e.g. 5" /></div>
          </div>}
        </div>
      </SectionCard>
    );
  }

  function FoodStep() {
    return (
     <SectionCard title="PlateChoice" quote="Nourish yourself and the planet gently." variant="food" badgeEmoji="🥗">
  <div className="fields-grid">
    <div className="field">
      <label className="label">Beef (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.meat.beef}
          onChange={(e) => updateFood("meat", "beef", e.target.value)}
          placeholder="0" />
      </div>
    </div>

    <div className="field">
      <label className="label">Chicken (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.meat.chicken}
          onChange={(e) => updateFood("meat", "chicken", e.target.value)}
          placeholder="0" />
      </div>
    </div>

    <div className="field">
      <label className="label">Pork (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.meat.pork}
          onChange={(e) => updateFood("meat", "pork", e.target.value)}
          placeholder="0" />
      </div>
    </div>

    <div className="field">
      <label className="label">Fish (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.meat.fish}
          onChange={(e) => updateFood("meat", "fish", e.target.value)}
          placeholder="0" />
      </div>
    </div>

    <div className="field">
      <label className="label">Milk (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.dairy.milk}
          onChange={(e) => updateFood("dairy", "milk", e.target.value)}
          placeholder="3.5" />
      </div>
    </div>

    <div className="field">
      <label className="label">Cheese (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.dairy.cheese}
          onChange={(e) => updateFood("dairy", "cheese", e.target.value)}
          placeholder="0.1" />
      </div>
    </div>

    <div className="field">
      <label className="label">Vegetables (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.plants.vegetables}
          onChange={(e) => updateFood("plants", "vegetables", e.target.value)}
          placeholder="5" />
      </div>
    </div>

    <div className="field">
      <label className="label">Fruits (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.plants.fruits}
          onChange={(e) => updateFood("plants", "fruits", e.target.value)}
          placeholder="5" />
      </div>
    </div>

    <div className="field">
      <label className="label">Grains (kg / week)</label>
      <div className="control">
        <input className="paper-input" type="number" inputMode="numeric"
          value={food.plants.grains}
          onChange={(e) => updateFood("plants", "grains", e.target.value)}
          placeholder="5" />
      </div>
    </div>
  </div>
</SectionCard>

    );
  }

  function WasteStep() {
    return (
      <SectionCard title="YourWaste" quote="Waste less, care more." variant="waste" badgeEmoji="♻️">
        <div>
          <div className="control-row">
            <div className="label">Plastic level</div>
            <div className="control"><select className="paper-select" value={waste.levels.plastic} onChange={(e) => updateWasteLevel("plastic", e.target.value)}>
              <option value="none">none</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Recycle plastic?</div>
            <div className="control"><select className="paper-select" value={waste.recycling.plastic} onChange={(e) => updateWasteRecycle("plastic", e.target.value)}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Paper level</div>
            <div className="control"><select className="paper-select" value={waste.levels.paper} onChange={(e) => updateWasteLevel("paper", e.target.value)}>
              <option value="none">none</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Recycle paper?</div>
            <div className="control"><select className="paper-select" value={waste.recycling.paper} onChange={(e) => updateWasteRecycle("paper", e.target.value)}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Glass level</div>
            <div className="control"><select className="paper-select" value={waste.levels.glass} onChange={(e) => updateWasteLevel("glass", e.target.value)}>
              <option value="none">none</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Recycle glass/metal?</div>
            <div className="control"><select className="paper-select" value={waste.recycling.glass} onChange={(e) => updateWasteRecycle("glass", e.target.value)}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Organic level</div>
            <div className="control"><select className="paper-select" value={waste.levels.organic} onChange={(e) => updateWasteLevel("organic", e.target.value)}>
              <option value="none">none</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select></div>
          </div>

          <div className="control-row">
            <div className="label">Compost organics?</div>
            <div className="control"><select className="paper-select" value={waste.compost} onChange={(e) => setWaste((w) => ({ ...w, compost: e.target.value }))}>
              <option value="no">no</option>
              <option value="yes">yes</option>
            </select></div>
          </div>
        </div>
      </SectionCard>
    );
  }

  function ResultsPanel() {
  if (!results) return null;
  return (
    <div className="paper-card variant-results">
      <div className="section-title">🌍 Your Eco Impact</div>
      <div className="card-quote">Keep working toward a greener planet — every small step matters! 🌱</div>

      <div className="results-summary">
        <div className="result-box">
          <span className="result-emoji">📅</span>
          <div>
            <div className="result-label">Weekly total</div>
            <div className="result-value">{results.summary.total_weekly_kg_co2.toFixed(2)} kg CO₂</div>
          </div>
        </div>

        <div className="result-box">
          <span className="result-emoji">🗓️</span>
          <div>
            <div className="result-label">Annual total</div>
            <div className="result-value">{results.summary.total_annual_kg_co2.toFixed(1)} kg CO₂</div>
          </div>
        </div>

        <div className="result-box">
          <span className="result-emoji">🏆</span>
          <div>
            <div className="result-label">Highest Category</div>
            <div className="result-value">{results.summary.highest_category}</div>
          </div>
        </div>
      </div>
    

      <h4 className="muted-label" style={{ marginTop: "20px" }}>Breakdown by Category</h4>
      <div className="breakdown-horizontal">
        {["transportation", "energy", "food", "waste"].map((cat) => (
          <div key={cat} className="breakdown-item">
            <div className="breakdown-emoji">
              {cat === "transportation" && "🚗"}
              {cat === "energy" && "⚡"}
              {cat === "food" && "🥗"}
              {cat === "waste" && "♻️"}
            </div>
            <div className="breakdown-text">
              <strong>{cat}</strong>
              <div>{results[cat].weekly_kg_co2.toFixed(2)} kg/week</div>
              <div>{results[cat].annual_kg_co2.toFixed(1)} kg/year</div>
            </div>
          </div>
        ))}
      </div>
      {/* GET SUGGESTIONS BUTTON  */}
      <div style={{ marginTop: 16, display: "flex", gap: 8, justifyContent: "center" }}>
        <button
          className="warm-btn"
          onClick={() => {
            try {
              const payload = buildPayload();
              localStorage.setItem("last_payload", JSON.stringify(payload));
              localStorage.setItem("last_calc", JSON.stringify(results));
              navigate("/suggestions", { state: { payload, results } });
            } catch (err) {
              console.warn("Failed to navigate to suggestions:", err);
            }
          }}
        >
          Get Habit Suggestions
        </button>
      </div>

    </div>
  );
}


  // main render
  return (
    <div className="app-parchment">
      <div style={{ maxWidth: 920, margin: "0 auto" }}>
        {/* title area: show current category name below navbar (no step text) */}
        
        {/* centered stage */}
        <div className="calc-stage">
          <div style={{ width: "100%", maxWidth: 920 }}>
            {step === 0 && <TransportStep />}
            {step === 1 && <EnergyStep />}
            {step === 2 && <FoodStep />}
            {step === 3 && <WasteStep />}
            {step === 4 && <ResultsPanel />}
          </div>
        </div>

        {/* error */}
        {error && <div className="paper-card" style={{ marginTop: 12, borderLeft: "4px solid #b43e3e" }}>{error}</div>}

        {/* controls */}
        <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 18 }}>
          <button type="button" onClick={goBack} className="warm-btn-ghost" disabled={step === 0 && !results}>Back</button>

          {step < 3 && <button type="button" onClick={goNext} className="warm-btn">Next</button>}

          {step === 3 && (
            <>
              <button type="button" onClick={() => setStep(4)} className="warm-btn-ghost">Review</button>
              <button type="button" onClick={handleCalculate} className="warm-btn" disabled={loading}>{loading ? "Calculating…" : "Calculate"}</button>
            </>
          )}

          {step === 4 && (
            <>
              <button type="button" onClick={() => { setResults(null); setStep(0); }} className="warm-btn-ghost">Start Over</button>
              <button type="button" onClick={() => setStep(3)} className="warm-btn-ghost">Edit Inputs</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
