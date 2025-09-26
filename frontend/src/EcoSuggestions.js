import React from 'react';

const ecoTips = [
  {
    id: 'transport',
    check: (inputs) => parseFloat(inputs.travel) > 3 || parseFloat(inputs.carKm) > 100,
    tip: "Try public transport twice a week 🚇",
  },
  {
    id: 'meat',
    check: (inputs) => inputs.food === 'highMeat',
    tip: "Go for a meat-free Monday 🌱",
  },
  {
    id: 'energy',
    check: (inputs) => parseFloat(inputs.energy) > 400,
    tip: "Switch off unused appliances to save energy 💡",
  },
  {
    id: 'general',
    check: () => true,
    tip: "Reduce, reuse, recycle ♻️",
  },
];

function shuffle(array) {
  return array.sort(() => Math.random() - 0.5);
}

export default function EcoSuggestions({ inputs }) {
  if (!inputs) return null;

  // Filter tips for those that match user input
  let relevant = ecoTips.filter(tip => tip.check(inputs));
  relevant = shuffle(relevant);

  return (
    <div style={{ maxWidth: 400, margin: '30px auto', padding: 10, textAlign: 'center' }}>
      <h3>Eco Habit Suggestions</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {relevant.map((tip, i) => (
          <div key={i} style={{
            background: '#e0ffe0',
            borderRadius: 10,
            boxShadow: '0 2px 6px #ccc',
            padding: '10px 16px',
            fontSize: '1.1rem',
            fontWeight: '500'
          }}>
            {tip.tip}
          </div>
        ))}
      </div>
    </div>
  );
}
