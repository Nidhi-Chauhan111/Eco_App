
// src/Navbar.jsx
import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./App.css";

const API_BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";
const STATIC_PROFILE = "/static/images/default_profile.png"; // put this file in public/static/images/

export default function Navbar({ theme, toggleTheme }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("access_token") || localStorage.getItem("token");
      if (!token) { setLoadingUser(false); return; }

      try {
        const res = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        // If backend returns 401/404 -> treat as not authenticated
        if (res.status === 401 || res.status === 404) {
          console.warn("No current user (status)", res.status);
          // Optionally redirect to login on 401
          if (res.status === 401) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("token");
            navigate("/login");
          }
          setUser(null);
          return;
        }

        if (!res.ok) {
          console.warn("Failed to load user:", res.status);
          setUser(null);
          return;
        }

        const data = await res.json();
        setUser(data);
      } catch (err) {
        console.error("Error loading user:", err);
        setUser(null);
      } finally {
        setLoadingUser(false);
      }
    }
    loadUser();
  }, [navigate]);

  const logoutBackendIfAvailable = async () => {
    // If you have a server-side logout route you want to hit, enable it here.
    // If not, it's fine to skip and simply clear tokens client-side.
    const token = localStorage.getItem("access_token") || localStorage.getItem("token");
    if (!token) return;
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }
      });
      // ignore response — we proceed to clear client tokens regardless
    } catch (err) {
      // silent: backend logout not required
    }
  };

  const handleLogout = async () => {
    await logoutBackendIfAvailable();
    localStorage.removeItem("access_token");
    localStorage.removeItem("token");
    // If you kept any user-specific local storage keys, clear them too:
    // localStorage.removeItem("last_payload"); localStorage.removeItem("last_calc"); etc.
    setUser(null);
    setMenuOpen(false);
    navigate("/login");
  };

  const linkClass = (path) => "nav-link" + (location.pathname === path ? " active-link" : "");
  const profileImg = user?.profile_pic_url ? user.profile_pic_url : STATIC_PROFILE;
  const displayName = user?.name || user?.email?.split?.("@")?.[0] || "Guest";

  return (
    <>
      <nav className={`navbar ${theme}`}>
        <div className="logo">🌿 CANOPY</div>
        <div className="links">
          <Link to="/" className={linkClass("/")}>Home</Link>
          <Link to="/Calculator" className={linkClass("/Calculator")}>Calculator</Link>
          <Link to="/Suggestions" className={linkClass("/Suggestions")}>Suggestions</Link>
          <Link to="/Journal" className={linkClass("/Journal")}>Journal</Link>

          <button onClick={toggleTheme} aria-label="Toggle theme" className="theme-toggle" title="Toggle theme">
            {/* icon */}
          </button>

          <button className="menu-icon" onClick={() => setMenuOpen(!menuOpen)} aria-label="User menu" title="User menu">☰</button>
        </div>
      </nav>

      {menuOpen && (
        <div className={`user-popup ${theme}`}>
          <div className="user-popup-header">
            <div className="profile-pic-container">
              <img
                src={profileImg}
                alt="Profile"
                className="profile-pic"
                onError={(e) => { e.target.onerror = null; e.target.src = STATIC_PROFILE; }}
                style={{ cursor: "default" }}
              />
            </div>

            <div className="user-info">
              <p className="user-email">{user?.email || "Not signed in"}</p>
              <p className="user-greeting">Hello, {displayName}</p>
            </div>
          </div>

          <div className="user-popup-actions">
            {/* PROFILE button removed as requested */}
            <button onClick={handleLogout} className="popup-btn logout-btn">Log Out</button>
          </div>
        </div>
      )}
    </>
  );
}
