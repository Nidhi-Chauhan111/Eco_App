import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './Navbar';
import Login from './login';
import Page1 from './Page1';
import Page2 from './Page2';
import Page3 from './Page3';

export default function App() {
  const [user, setUser] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  function handleLogin(userData) {
    setUser(userData);
  }

  function handleLogout() {
    setUser(null);
  }

  return (
    <Router>
      <Navbar darkMode={darkMode} toggleDarkMode={() => setDarkMode(!darkMode)} />
      <div style={{
        paddingTop: 70,
        minHeight: "calc(100vh - 70px)",
        backgroundColor: darkMode ? "#121212" : "#f9fafb",
        color: darkMode ? "#ddd" : "#000",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}>
        <Routes>
          {!user && (
            <Route path="/*" element={<Login onLogin={handleLogin} />} />
          )}
          {user && (
            <>
              <Route path="/page1" element={<Page1 />} />
              <Route path="/page2" element={<Page2 />} />
              <Route path="/page3" element={<Page3 />} />
              <Route path="/" element={<Navigate to="/page1" />} />
            </>
          )}
          <Route path="*" element={<Navigate to={user ? "/page1" : "/"} />} />
        </Routes>
      </div>
    </Router>
  );
}
