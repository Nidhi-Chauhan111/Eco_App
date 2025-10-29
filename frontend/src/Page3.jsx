import React, { useEffect } from "react";
import { motion } from "framer-motion";
import "./App.css";

const suggestions = [
  {
    title: "Use Public Transport 🚍",
    description:
      "Reduce your carbon footprint by taking buses, trains, or carpooling instead of driving alone.",
    color: "#D1FADF",
  },
  {
    title: "Save Electricity 💡",
    description:
      "Turn off lights and unplug devices when not in use. Switch to LED bulbs to save energy.",
    color: "#CFFAFE",
  },
  {
    title: "Eat More Plant-Based 🌿",
    description:
      "Incorporate more fruits, vegetables, and grains into your meals to reduce food emissions.",
    color: "#FDE68A",
  },
  {
    title: "Recycle & Reuse ♻️",
    description:
      "Sort your waste properly, recycle plastics and glass, and reuse materials when possible.",
    color: "#E0E7FF",
  },
  {
    title: "Conserve Water 💧",
    description:
      "Take shorter showers and fix leaks — small steps that save both water and energy.",
    color: "#FCE7F3",
  },
  {
    title: "Plant Trees 🌳",
    description:
      "Planting even a few trees can absorb CO₂ and improve air quality around your home.",
    color: "#FBCFE8",
  },
];

function Page3() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="suggestion-page">
      <motion.h2
        className="suggestion-title"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        🌍 Eco-Friendly Suggestions
      </motion.h2>
      <motion.p
        className="suggestion-subtitle"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.7 }}
      >
        Small actions make a big impact — start today!
      </motion.p>

      <div className="suggestion-grid">
        {suggestions.map((tip, index) => (
          <motion.div
            key={index}
            className="suggestion-card"
            style={{ backgroundColor: tip.color }}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2 }}
            whileHover={{ scale: 1.05, rotate: -1 }}
          >
            <h3>{tip.title}</h3>
            <p>{tip.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default Page3;
