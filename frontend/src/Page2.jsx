import React from "react";
import CalculatorComponent from "./CalculatorComponent"; // import the UI you just created

export default function Page2() {
  return (
    <div>
      {/* You can set your backend API URL here */}
      <CalculatorComponent apiUrl="http://127.0.0.1:8000/api/calculate" />
    </div>
  );
}
