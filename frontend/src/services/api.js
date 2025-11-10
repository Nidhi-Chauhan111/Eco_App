// frontend/src/services/api.js
// Mock API client for Calculator. Replace `mockCalculate` with a real fetch to your backend endpoint.

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";

function mockCalculate(payload) {
  // This mock mimics backend.calculate_from_payload behaviour:
  // returns weekly and annual per category and a summary (total_weekly, total_annual, highest_category).
  // For realistic demo, we apply same simple factors as backend (approx).
  const sumWeekly = (o) => Object.values(o || {}).reduce((a, b) => a + (Number(b) || 0), 0);

  // transport: expect km_per_week or flights converted inside backend; we'll approximate here
  const transport =
    (payload.transportation?.car?.km_per_week || 0) * 0.23 +
    (payload.transportation?.bus?.km_per_week || 0) * 0.09 +
    (payload.transportation?.train?.km_per_week || 0) * 0.03 +
    ((payload.transportation?.flights?.domestic_per_year || 0) * 1000 * 0.13 +
      (payload.transportation?.flights?.international_per_year || 0) * 8000 * 0.10) /
      52;

  // energy: monthly -> weekly using backend ratio monthly*(12/52)
  const elecFactor = {
    "Electricity (US Grid Average)": 0.45,
    "Electricity (Coal-heavy)": 0.7,
    "Electricity (Natural Gas)": 0.4,
    "Electricity (Renewable)": 0.1,
  }[payload.energy?.electricity?.grid_type] || 0.45;

  const electricityWeekly =
    ((payload.energy?.electricity?.kwh_per_month || 0) * elecFactor * (12 / 52)) || 0;

  const gasWeekly =
    ((payload.energy?.natural_gas?.scf_per_month || 0) * 0.0544 * (12 / 52)) || 0;

  const lpgWeekly =
    ((payload.energy?.lpg?.gallons_per_month || 0) * 5.72 * (12 / 52)) || 0;

  const energy = electricityWeekly + gasWeekly + lpgWeekly;

  // food: using backend factors per kg/week
  const f = payload.food || {};
  const meat = (f.meat?.beef || 0) * 27 + (f.meat?.chicken || 0) * 6.9 + (f.meat?.pork || 0) * 7.2 + (f.meat?.fish || 0) * 2.9;
  const dairy = (f.dairy?.milk || 0) * 3.3 + (f.dairy?.cheese || 0) * 13.5;
  const plants = (f.plants?.vegetables || 0) * 0.4 + (f.plants?.fruits || 0) * 0.7 + (f.plants?.grains || 0) * 2.7;
  const food = meat + dairy + plants;

  // waste: map levels to bins and multiply with default factor (approx)
  const bins = {
    plastic: { none: 0.0, low: 0.12, medium: 0.4, high: 0.8 },
    paper: { none: 0.0, low: 0.5, medium: 1.5, high: 3.0 },
    glass: { none: 0.0, low: 0.3, medium: 0.8, high: 1.5 },
    metal: { none: 0.0, low: 0.2, medium: 0.6, high: 1.2 },
    organic: { none: 0.0, low: 2.0, medium: 4.0, high: 7.0 },
  };

  const levels = payload.waste?.levels || {};
  const rec = payload.waste?.recycling || {};
  const compost = payload.waste?.compost === "yes";

  const w_plastic = (bins.plastic[levels.plastic || "none"] || 0) * (rec.plastic === "yes" ? 2.1 : 3.0);
  const w_paper = (bins.paper[levels.paper || "none"] || 0) * (rec.paper === "yes" ? 0.5 : 1.0);
  const w_glass = (bins.glass[levels.glass || "none"] || 0) * (rec.glass === "yes" ? 0.64 : 0.85);
  const w_metal = (bins.metal[levels.metal || "none"] || 0) * (rec.metal === "yes" ? 1.5 : 2.0);
  const w_org = (bins.organic[levels.organic || "none"] || 0) * (compost ? 0.1 : 0.5);

  const waste = w_plastic + w_paper + w_glass + w_metal + w_org;

  const total_weekly = transport + energy + food + waste;
  const total_annual = total_weekly * 52;

  const results = {
    transportation: { weekly_kg_co2: Number(transport.toFixed(3)), annual_kg_co2: Number((transport * 52).toFixed(2)) },
    energy: { weekly_kg_co2: Number(energy.toFixed(3)), annual_kg_co2: Number((energy * 52).toFixed(2)) },
    food: { weekly_kg_co2: Number(food.toFixed(3)), annual_kg_co2: Number((food * 52).toFixed(2)) },
    waste: { weekly_kg_co2: Number(waste.toFixed(3)), annual_kg_co2: Number((waste * 52).toFixed(2)) },
    summary: {
      total_weekly_kg_co2: Number(total_weekly.toFixed(3)),
      total_annual_kg_co2: Number(total_annual.toFixed(2)),
      highest_category: ["transportation","energy","food","waste"].reduce((a,b) => {
        const vals = { transportation: transport, energy, food, waste };
        return vals[a] > vals[b] ? a : b;
      }, "transportation")
    }
  };

  // Optionally include recommendations if you want (backend can supply later)
  results.recommendations = [
    "This is a demo recommendation. Replace with backend recommendations when available."
  ];

  return new Promise((resolve) => setTimeout(() => resolve({ data: results }), 600));
}

export async function submitCalculator(payload) {
  // Replace with a real network call when ready:
  // return fetch(`${API_BASE}/api/calculate`, { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
  //         .then(r => r.json());

  // For now use the mock
  const res = await mockCalculate(payload);
  return res.data;
}
