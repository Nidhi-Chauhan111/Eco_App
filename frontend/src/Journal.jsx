import React, { useState } from "react";
import "./App.css";

function Journal() {
  const [entry, setEntry] = useState("");
  const [entries, setEntries] = useState([]);

  const handleAddEntry = (e) => {
    e.preventDefault();
    if (entry.trim()) {
      const newEntry = {
        id: Date.now(),
        text: entry,
        date: new Date().toLocaleString(),
      };
      setEntries([newEntry, ...entries]);
      setEntry("");
    }
  };

  const handleDelete = (id) => {
    setEntries(entries.filter((entry) => entry.id !== id));
  };

  return (
    <div className="journal-container">
      <div className="journal-header">
        <h1>🌿 Eco Journal</h1>
        <p>
          Reflect on your sustainable choices and small victories each day.  
          Every note brings you closer to a greener lifestyle 🍃
        </p>
      </div>

      <form className="journal-form" onSubmit={handleAddEntry}>
        <textarea
          value={entry}
          onChange={(e) => setEntry(e.target.value)}
          placeholder="Write about your eco-friendly action today..."
        />
        <button type="submit" className="journal-btn">Add Entry</button>
      </form>

      <div className="entries-list">
        {entries.length === 0 ? (
          <p className="empty-msg">No journal entries yet 🌎</p>
        ) : (
          entries.map((item) => (
            <div key={item.id} className="entry-card fade-in">
              <p>{item.text}</p>
              <div className="entry-meta">
                <span>{item.date}</span>
                <button onClick={() => handleDelete(item.id)}>🗑️</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Journal;
