import React, { useState } from "react";
import Navbar from "./Navbar";
import carbonFootprintImg from "./carbon-footprint.jpg"; // Ensure this exists!

const FloatingLabelInput = ({
  label,
  id,
  type = "text",
  value,
  onChange,
  required = false,
  showPasswordToggle = false,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const floatLabel = isFocused || value.length > 0;
  const inputType = showPasswordToggle ? (showPassword ? "text" : "password") : type;

  return (
    <div style={{ position: "relative", marginBottom: 24 }}>
      <input
        id={id}
        type={inputType}
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        required={required}
        className="fancy-input"
        style={{
          width: "100%",
          padding: showPasswordToggle ? "15px 40px 15px 15px" : "15px",
          fontSize: 17,
          borderRadius: 11,
          border: "1.8px solid #b9f0d8",
          background: "#fafffb",
          boxSizing: "border-box",
          transition: "border-color .21s, box-shadow .2s, background 0.17s"
        }}
      />
      <label
        htmlFor={id}
        style={{
          position: "absolute",
          left: 18,
          top: floatLabel ? -12 : 17,
          fontSize: floatLabel ? 12 : 17,
          color: "#12916B",
          fontWeight: "bold",
          backgroundColor: "#fafffb",
          padding: "0 7px",
          borderRadius: 7,
          transition: "all 0.2s cubic-bezier(.8,.32,0,1)",
          pointerEvents: "none",
          userSelect: "none",
        }}
      >
        {label}
      </label>
      {showPasswordToggle && (
        <button
          type="button"
          onClick={() => setShowPassword((s) => !s)}
          aria-label={showPassword ? "Hide password" : "Show password"}
          style={{
            position: "absolute",
            right: 13,
            top: "53%",
            transform: "translateY(-50%)",
            background: "none",
            border: "none",
            cursor: "pointer",
            color: "#006e4e",
            fontWeight: "bold",
            userSelect: "none",
            fontSize: 19,
            opacity: 0.8,
            transition: "opacity .18s"
          }}
        >
          {showPassword ? "🙈" : "👁️"}
        </button>
      )}
    </div>
  );
};

export default function Login({ onLogin }) {
  const [showSignup, setShowSignup] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [signupName, setSignupName] = useState("");
  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");

  const toggleForm = () => setShowSignup((prev) => !prev);
  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  const handleLogin = (event) => {
    event.preventDefault();
    if (onLogin) onLogin({ name: loginEmail || "Aishwarya Panda" });
  };

  const handleSignup = (event) => {
    event.preventDefault();
    setShowSignup(false);
  };

  const containerStyle = {
    minHeight: "100vh",
    paddingTop: "65px", // Padding for navbar (navbar is 60px height)
    backgroundColor: darkMode ? "#121212" : "transparent",
    color: darkMode ? "#ddd" : "#126644",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    gap: 60,
    padding: "50px",
    paddingTop: "115px", // Adds space for fixed nav
    transition: "all 0.3s",
    background: darkMode
      ? "#121212"
      : "linear-gradient(120deg,#f9fafb 0,#ddf3e4 50%,#ecfdf3 100%)",
  };

  const leftPanelStyle = {
    maxWidth: 410,
    backgroundColor: darkMode ? "#133822" : "#e6f3da",
    borderRadius: 28,
    padding: 36,
    boxShadow: "0 8px 28px #b2e2c98a",
    textAlign: "center",
    userSelect: "none",
    minHeight: 370,
  };

  const rightPanelStyle = {
    width: 300,
    backgroundColor: darkMode ? "#1d3e27" : "#fff",
    borderRadius: 28,
    padding: 36,
    boxShadow: "0 8px 28px #b2e2c98a",
    color: darkMode ? "#caeabe" : "#207332",
    userSelect: "none",
    minHeight: 300,
  };

  const buttonStyle = {
    width: "100%",
    padding: 12,
    borderRadius: 13,
    border: "none",
    backgroundColor: "#2b7a3b",
    color: "white",
    cursor: "pointer",
    fontWeight: "bold",
    fontSize: 17
  };

  const linkStyle = {
    marginTop: 15,
    color: darkMode ? "#a7d99e" : "#2b7b32",
    cursor: "pointer",
    fontWeight: "600",
    textAlign: "center",
    fontSize: 15,
    userSelect: "none",
  };

  return (
    <>
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      <div style={containerStyle}>
        {/* Info Panel */}
        <div className="animated-card" style={leftPanelStyle}>
          <img
            src={carbonFootprintImg}
            alt="Carbon Footprint"
            style={{
              width: 110,
              marginBottom: 25,
              borderRadius: 10,
              boxShadow: "0 2px 10px #b2e2caa1"
            }}
          />
          <h2 style={{ margin: "16px 0 11px", fontSize: 27, fontWeight: "bold" }}>
            What is a Carbon Footprint?
          </h2>
          <p style={{ marginTop: 15, lineHeight: 1.58, fontWeight: "500" }}>
            Your carbon footprint measures the greenhouse gases your daily activities create,
            such as eating, traveling, and energy use.
            By making sustainable choices, you help protect the planet.
          </p>
          <button
            onClick={toggleDarkMode}
            style={{
              marginTop: 30,
              padding: "13px 20px",
              borderRadius: 16,
              border: "none",
              background:
                darkMode
                  ? "linear-gradient(90deg,#4c9c60 10%,#4daf73 90%)"
                  : "linear-gradient(90deg,#1da549 10%,#2bb550 90%)",
              color: "#fff",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: 17,
              boxShadow: "0 4px 15px #8bceac95"
            }}
          >
            {darkMode ? "Light Mode" : "Dark Mode"} 🌙
          </button>
        </div>

        {/* Right Panel */}
        <div className="animated-card animated-card--delay" style={rightPanelStyle}>
          {showSignup ? (
            <>
              <h2 style={{ textAlign: "center", marginBottom: 18, fontWeight: "bold", fontSize: 25 }}>
                Sign Up 🌿
              </h2>
              <form onSubmit={handleSignup}>
                <FloatingLabelInput
                  label="Full Name"
                  id="signup-name"
                  value={signupName}
                  onChange={e => setSignupName(e.target.value)}
                  required
                />
                <FloatingLabelInput
                  label="Email"
                  id="signup-email"
                  type="email"
                  value={signupEmail}
                  onChange={e => setSignupEmail(e.target.value)}
                  required
                />
                <FloatingLabelInput
                  label="Password"
                  id="signup-password"
                  type="password"
                  value={signupPassword}
                  onChange={e => setSignupPassword(e.target.value)}
                  required
                  showPasswordToggle
                />
                <button type="submit" style={buttonStyle}>
                  Sign Up
                </button>
              </form>
              <div onClick={toggleForm} style={linkStyle}>
                Already have an account? Log In
              </div>
            </>
          ) : (
            <>
              <h2 style={{ textAlign: "center", marginBottom: 18, fontWeight: "bold", fontSize: 25 }}>
                Login 🌿
              </h2>
              <form onSubmit={handleLogin}>
                <FloatingLabelInput
                  label="Email or Username"
                  id="login-email"
                  value={loginEmail}
                  onChange={e => setLoginEmail(e.target.value)}
                  required
                />
                <FloatingLabelInput
                  label="Password"
                  id="login-password"
                  type="password"
                  value={loginPassword}
                  onChange={e => setLoginPassword(e.target.value)}
                  required
                  showPasswordToggle
                />
                <button type="submit" style={buttonStyle}>
                  Login
                </button>
              </form>
              <div onClick={toggleForm} style={linkStyle}>
                Don't have an account? Sign Up
              </div>
            </>
          )}
        </div>
      </div>
    </>
  );
}
