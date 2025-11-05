import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./App.css";
import carbonFootprint from "./canopy.jpeg"; // your image

function Page1() {
  const navigate = useNavigate();

  return (
    <div className="home-section">
      {/* Floating eco icons */}
      <div className="floating-icons">
        <span>🌿</span>
        <span>🌎</span>
        <span>🌞</span>
        <span>💧</span>
      </div>

      <motion.div
        className="home-content"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <div className="home-text">
          <h1 className="home-title">
            Track Your <span>Carbon Footprint</span>
          </h1>
          <p className="home-desc">
            Understand the impact of your lifestyle choices and take small steps
            toward a sustainable future. Together, we can make a greener planet.
          </p>
          <motion.button
            className="cta-btn"
            onClick={() => navigate("/login")}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            🌱 Login or Sign Up
          </motion.button>
        </div>

        <motion.div
          className="home-image"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
        >
          <img src={carbonFootprint} alt="Carbon Footprint" />
        </motion.div>
      </motion.div>
    </div>
  );
}

export default Page1;
