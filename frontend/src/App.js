import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Navbar";
import Page1 from "./Page1";
import Page2 from "./Page2";
import EcoSuggestions from "./EcoSuggestions";
import Login from "./login";
import Journal from "./Journal"; // ✅ add this line
import "./App.css";


function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Page1 />} />
        <Route path="/calculator" element={<Page2 />} />
        <Route path="/suggestions" element={<EcoSuggestions/>} />
        <Route path="/login" element={<Login />} />
        <Route path="/journal" element={<Journal />} /> {/* ✅ add this */}
      </Routes>
    </Router>
  );
}

export default App;