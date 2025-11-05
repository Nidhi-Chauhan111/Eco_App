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
      <div className="logo">🌿 CANOPY</div>
      <div className="links">
        <Link to="/" className={linkClass("/")}>Home</Link>
        <Link to="/Calculator" className={linkClass("/Calculator")}>Calculator</Link>
        <Link to="/Suggestions" className={linkClass("/Suggestions")}>Suggestions</Link>
        <Link to="/Journal" className={linkClass("/Journal")}>Journal</Link>
        
        
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
