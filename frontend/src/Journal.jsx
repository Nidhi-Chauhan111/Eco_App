// Journal.jsx (updated)
import React, { useState } from "react";
import { Send } from "lucide-react";

export default function Journal() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: "bot",
      text: "🌱 Hey there! How was your day today? Did you do something eco-friendly?",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() === "") return;
    const newMessage = { id: Date.now(), sender: "user", text: input };
    const ecoResponses = [
      "That’s wonderful! Every small step counts 🌿",
      "Awesome! Reflecting on your day helps you grow greener habits 🌎",
      "Keep it up! Your choices make a difference 🌱",
      "Beautiful! Sustainability starts with mindfulness 🌻",
      "Great job! Let’s make tomorrow even greener 💚",
    ];
    const randomResponse = ecoResponses[Math.floor(Math.random() * ecoResponses.length)];
    setMessages((prev) => [...prev, newMessage, { id: Date.now() + 1, sender: "bot", text: randomResponse }]);
    setInput("");
  };

  return (
    <div className="journal-page abstract-bg">
      <div className="journal-container">
        <div className="journal-header">
          <h1>🌿 Eco Journal Chat</h1>
          <p>Share your day and reflect on eco-friendly steps.</p>
        </div>

        <div style={{ flex: 1, overflowY: "auto", marginBottom: "1rem" }}>
          {messages.map((msg) => (
            <div key={msg.id} style={{ display: "flex", justifyContent: msg.sender === "user" ? "flex-end" : "flex-start", marginBottom: 8 }}>
              <div style={{
                  padding: 12,
                  borderRadius: 16,
                  maxWidth: 520,
                  background: msg.sender === "user" ? "#037a3b" : "#fff",
                  color: msg.sender === "user" ? "#fff" : "#222",
                  border: msg.sender === "user" ? "none" : "1px solid rgba(3,122,59,0.06)"
                }}>
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        <div className="journal-form" style={{ display: "flex", gap: 8 }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Write about your day..."
            style={{ flex: 1, padding: "10px 14px", borderRadius: 12, border: "1px solid #b5eac5", outline: "none", background: "#f7fff9" }}
          />
          <button onClick={handleSend} className="journal-btn" aria-label="send">
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}