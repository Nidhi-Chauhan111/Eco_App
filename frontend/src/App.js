import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./Navbar";
import Page1 from "./Page1";
import Page2 from "./Page2";
import Page3 from "./Page3";
import Login from "./login";
import "./App.css";

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Page1 />} />
        <Route path="/calculator" element={<Page2 />} />
        <Route path="/suggestions" element={<Page3 />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </Router>
  );
}

export default App;
