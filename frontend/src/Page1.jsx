import React from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";
import logo from "./canopy.jpeg"; // ✅ correct logo path

const Page1 = () => {
  const navigate = useNavigate();
  const emojis = [ "🌻", "🍃", "🌱", "🌼", "🍂", "🌎"];

  return (
    <div className="page1-container">
      {/* 🌸 Floating Emojis */}
      {emojis.map((emoji, index) => (
        <span key={index} className={`floating-emoji emoji-${index}`}>
          {emoji}
        </span>
      ))}

      {/* 🌿 Main Content */}
      <div className="page1-content">
        <div className="text-content">
          <h1>
            🌸 Welcome to <span className="highlight">CAnoPY</span>
          </h1>
          <p className="tagline">
            <em>Reflect. Act. Grow Greener Every Day.</em>
          </p>
          <p className="desc">
            Track your <b>carbon footprint</b> and embrace a sustainable
            lifestyle. Let’s nurture our planet together — one small choice at a
            time. 🌎
          </p>
          <button className="journey-btn" onClick={() => navigate("/login")}>
            🌱 Begin Your Journey
          </button>
        </div>

        <div className="logo-container">
          <img src={logo} alt="CANoPY Logo" />
        </div>
      </div>
    </div>
  );
};

export default Page1;
