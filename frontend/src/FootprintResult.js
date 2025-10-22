import React from 'react';

function getEmoji(feet) {
  if (feet > 15) return '🌍😟';
  if (feet > 8) return '🌍😐';
  return '🌍😊';
}

export default function FootprintResult({ footprint }) {
  if (footprint === null) return null;
  const avgFootprint = 10;
  const percentDiff = (((footprint - avgFootprint) / avgFootprint) * 100).toFixed(1);
  const emoji = getEmoji(footprint);
  const progressPercent = Math.min((footprint / (avgFootprint * 2)) * 100, 100);

  return (
    <div style={{ maxWidth: 400, margin: '20px auto', textAlign: 'center' }}>
      <h3>Your Estimated Annual CO₂ Footprint</h3>
      <p><strong>{footprint.toFixed(2)} tons CO₂</strong></p>
      <p>Your footprint is {percentDiff}% {percentDiff > 0 ? 'above' : 'below'} average.</p>
      <div style={{
        background: '#ddd',
        borderRadius: 10,
        overflow: 'hidden',
        height: 20,
        margin: '10px 0'
      }}>
        <div style={{
          width: `${progressPercent}%`,
          height: '100%',
          backgroundColor: progressPercent > 70 ? '#e74c3c' : progressPercent > 40 ? '#f1c40f' : '#2ecc71',
          transition: 'width 0.5s ease'
        }} />
      </div>
      <div style={{ fontSize: '2rem' }}>
        {emoji}
      </div>
    </div>
  );
}
