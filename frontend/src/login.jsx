// Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css"; // Change this to any style file (LoginGlass.css, etc.)

function Login() {
  const [isSignup, setIsSignup] = useState(false);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: fullName, email, password }),
      });

      if (!response.ok) {
        const errData = await response.json();
        alert(`Signup failed: ${errData.detail || response.statusText}`);
        return;
      }

      const data = await response.json();
      alert(`Signup successful! Welcome, ${data.user}`);
      setIsSignup(false);
      setFullName("");
      setEmail("");
      setPassword("");
    } catch (error) {
      console.error("Signup Error:", error);
      alert("Signup failed. Please check backend connection.");
    }
  };

  const handleLogin = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errData = await response.json();
        alert(`Login failed: ${errData.detail || response.statusText}`);
        return;
      }

      const data = await response.json();
      alert("Login successful!");
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } catch (error) {
      console.error("Login Error:", error);
      alert("Login failed. Please check backend connection.");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isSignup ? "Create Account" : "Welcome Back"}</h2>
        <form
          className="auth-form"
          onSubmit={isSignup ? handleSignup : handleLogin}
        >
          {isSignup && (
            <input
              type="text"
              placeholder="Full Name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="auth-btn">
            {isSignup ? "Sign Up" : "Login"}
          </button>
        </form>

        <p className="toggle-text">
          {isSignup ? "Already have an account?" : "Don’t have an account?"}{" "}
          <span
            onClick={() => {
              setIsSignup(!isSignup);
              setFullName("");
              setEmail("");
              setPassword("");
            }}
          >
            {isSignup ? "Login" : "Sign Up"}
          </span>
        </p>

        <button className="back-btn" onClick={() => navigate("/")}>
          ⬅ Back to Home
        </button>
      </div>
    </div>
  );
}

export default Login;
