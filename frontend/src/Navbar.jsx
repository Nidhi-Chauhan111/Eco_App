// src/Navbar.jsx
import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./App.css";

export default function Navbar({ theme, toggleTheme, userEmail = "user@example.com" }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [profilePic, setProfilePic] = useState(
    localStorage.getItem("ecoProfilePic") || ""
  );

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleChangePassword = () => {
    alert("Password change feature coming soon!");
  };

  const handleProfilePicChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        localStorage.setItem("ecoProfilePic", reader.result);
        setProfilePic(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const linkClass = (path) =>
    "nav-link" + (location.pathname === path ? " active-link" : "");

  return (
    <>
      <nav className={`navbar ${theme}`}>
        <div className="logo">🌿 CAnoPY</div>
        <div className="links">
          <Link to="/" className={linkClass("/")}>Home</Link>
          <Link to="/Calculator" className={linkClass("/Calculator")}>Calculator</Link>
          <Link to="/Suggestions" className={linkClass("/Suggestions")}>Suggestions</Link>
          <Link to="/Journal" className={linkClass("/Journal")}>Journal</Link>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="theme-toggle"
            title="Toggle theme"
          >
            
          </button>

          {/* Hamburger Icon */}
          <button
            className="menu-icon"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="User menu"
            title="User menu"
          >
            ☰
          </button>
        </div>
      </nav>

      {/* User Popup */}
      {menuOpen && (
        <div className={`user-popup ${theme}`}>
          <div className="user-popup-header">
            <div className="profile-pic-container">
              {profilePic ? (
                <img
                  src={profilePic}
                  alt="Profile"
                  className="profile-pic"
                  onClick={() => document.getElementById("profile-upload").click()}
                />
              ) : (
                <div
                  className="profile-placeholder"
                  onClick={() => document.getElementById("profile-upload").click()}
                >
                  📸
                </div>
              )}
              <input
                type="file"
                id="profile-upload"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleProfilePicChange}
              />
            </div>

            <div className="user-info">
              <p className="user-email">{userEmail}</p>
              <p className="user-greeting">Hello, Aishwarya 🌸</p>
            </div>
          </div>

          <div className="user-popup-actions">
            <button onClick={handleChangePassword} className="popup-btn">
              Change Password
            </button>
            <button onClick={handleLogout} className="popup-btn logout-btn">
              Log Out
            </button>
          </div>
        </div>
      )}
    </>
  );
}
