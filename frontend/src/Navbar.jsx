// src/Navbar.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";
import "./App.css";

export default function Navbar({ theme, toggleTheme }) {
  const location = useLocation();

  const linkClass = (path) =>
    "nav-link" + (location.pathname === path ? " active-link" : "");

  return (
    <nav className="navbar">
      <div className="logo">🌿 EcoTrack</div>
      <div className="links">
        <Link to="/" className={linkClass("/")}>Home</Link>
        <Link to="/calculator" className={linkClass("/calculator")}>Calculator</Link>
        <Link to="/suggestions" className={linkClass("/suggestions")}>Suggestions</Link>
        <button
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="theme-toggle"
          title="Toggle theme"
        >
          {theme === "light" ? "🌙" : "☀️"}
        </button>
      </div>
    </nav>
  );
}
