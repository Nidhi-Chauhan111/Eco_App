import React, { useState } from "react";
// Optionally import CarbonCalculator, EcoSuggestion

export default function Dashboard({ user, onLogout }) {
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: darkMode ? "#182331" : "#f3f6f9",
        color: darkMode ? "#fff" : "#123",
      }}
    >
      {/* Left/Main Content */}
      <main style={{ flex: 1, padding: 40 }}>
        <div
          style={{
            marginBottom: 28,
            background: "#fff",
            borderRadius: 16,
            padding: 26,
            minHeight: 150,
            boxShadow: "0 0 8px #dce1e4",
          }}
        >
          <h2>Calculator</h2>
          {/* <CarbonCalculator /> */}
        </div>
        <div
          style={{
            background: "#fff",
            borderRadius: 16,
            padding: 26,
            minHeight: 120,
            boxShadow: "0 0 8px #dce1e4",
          }}
        >
          <h2>Suggestions</h2>
          {/* <EcoSuggestion /> */}
        </div>
      </main>
      {/* Sidebar - User Info & Actions */}
      <nav
        style={{
          width: 240,
          background: darkMode ? "#202a38" : "#eaf5ec",
          borderTopRightRadius: 18,
          borderBottomRightRadius: 18,
          boxShadow: "-2px 0 15px #e2e7ef",
          padding: 20,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <div style={{ fontSize: 44, margin: 16 }}>👤</div>
        <div style={{ fontWeight: "bold", marginBottom: 12 }}>{user?.name}</div>
        <button
          onClick={() => alert("Settings Clicked")}
          style={sideBtn}
        >
          Settings
        </button>
        <button onClick={() => setDarkMode((d) => !d)} style={sideBtn}>
          {darkMode ? "Light Mode" : "Dark Mode"}
        </button>
        <button onClick={onLogout} style={sideBtn}>
          Logout
        </button>
      </nav>
    </div>
  );
}

const sideBtn = {
  width: "100%",
  margin: "8px 0",
  padding: "10px",
  borderRadius: "8px",
  border: "none",
  background: "#49be8c",
  color: "#fff",
  fontWeight: "bold",
  cursor: "pointer",
  letterSpacing: 1,
};
