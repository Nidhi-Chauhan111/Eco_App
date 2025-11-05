import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Journal from "./Journal";
import "./App.css";

function Home() {
  return (
    <div className="page">
      <h1>🌍 Welcome to CANOPY</h1>
      <p>Track your carbon footprint and write about your day in the Journal.</p>
    </div>
  );
}

function Calculator() {
  return <div className="page"><h2>🧮 Carbon Calculator</h2></div>;
}

function Suggestions() {
  return <div className="page"><h2>💡 Eco Suggestions</h2></div>;
}

function App() {
  return (
    <Router>
      <nav className="navbar">
        <h2 className="logo">🌿 CANOPY</h2>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><Link to="/calculator">Calculator</Link></li>
          <li><Link to="/suggestions">Suggestions</Link></li>
          <li><Link to="/journal">Journal</Link></li>
        </ul>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/calculator" element={<Calculator />} />
        <Route path="/suggestions" element={<Suggestions />} />
        <Route path="/journal" element={<Journal />} />
      </Routes>
    </Router>
  );
}

export default App;
