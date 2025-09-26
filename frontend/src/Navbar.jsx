import React from 'react';
import { NavLink } from 'react-router-dom';

export default function Navbar({ darkMode, toggleDarkMode }) {
  return (
    <nav className={`top-navbar${darkMode ? ' dark' : ''}`}>
      <div className="nav-left">
        <span className="brand" role="img" aria-label="EcoTrack">🌿 EcoTrack</span>
        <NavLink to="/page1" className="nav-link" activeclassname="active">Page 1</NavLink>
        <NavLink to="/page2" className="nav-link" activeclassname="active">Page 2</NavLink>
        <NavLink to="/page3" className="nav-link" activeclassname="active">Page 3</NavLink>
      </div>
      <button
        className="dark-toggle-btn"
        onClick={toggleDarkMode}
        aria-label={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      >
        {darkMode ? '☀️' : '🌙'}
      </button>
    </nav>
  );
}
