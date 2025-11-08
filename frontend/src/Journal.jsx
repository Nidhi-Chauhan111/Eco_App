import React, { useState, useEffect } from "react";
import "./App.css";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Journal() {
  const [entry, setEntry] = useState("");
  const [entries, setEntries] = useState([]);
  const [mood, setMood] = useState("");
  const [streak, setStreak] = useState(0);
  const [lastDate, setLastDate] = useState("");
  const [quote, setQuote] = useState("");
  const [sentiment, setSentiment] = useState("Neutral");
  const [showPopup, setShowPopup] = useState(false); // ⭐ ADDED

  const moods = [
    { emoji: "😊", label: "Happy" },
    { emoji: "😌", label: "Calm" },
    { emoji: "😢", label: "Sad" },
    { emoji: "😤", label: "Stressed" },
    { emoji: "🌿", label: "Peaceful" },
  ];

  // 🌿 Load stored data on mount
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("ecoJournalEntries")) || [];
    const savedStreak = localStorage.getItem("ecoJournalStreak");
    const savedLastDate = localStorage.getItem("ecoJournalLastDate");

    setEntries(stored);
    if (savedStreak) setStreak(parseInt(savedStreak, 10));
    if (savedLastDate) setLastDate(savedLastDate);
  }, []);

  // 🌞 Daily Inspirational Quote
  useEffect(() => {
    const today = new Date().toISOString().split("T")[0];
    const saved = JSON.parse(localStorage.getItem("ecoJournalQuote"));

    if (saved && saved.date === today) {
      setQuote(saved.text);
    } else {
      const quotes = [
        "Every small step counts toward a greener planet 🌿",
        "Nature always wears the colors of the spirit 🌈",
        "Plant dreams, pull weeds, and grow a happy life 🌱",
        "The Earth is what we all have in common 🌍",
        "You are blooming at your own pace 🌸",
      ];
      const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
      setQuote(randomQuote);
      localStorage.setItem(
        "ecoJournalQuote",
        JSON.stringify({ date: today, text: randomQuote })
      );
    }
  }, []);

  // 💖 Sentiment Analysis
  const analyzeSentiment = (text) => {
    const positiveWords = [
      "happy",
      "great",
      "love",
      "joy",
      "peace",
      "calm",
      "excited",
      "grateful",
      "wonderful",
      "good",
      "awesome",
    ];
    const negativeWords = [
      "sad",
      "angry",
      "tired",
      "stress",
      "upset",
      "bad",
      "worried",
      "anxious",
      "hate",
      "cry",
    ];

    const lower = text.toLowerCase();
    let score = 0;

    positiveWords.forEach((w) => {
      if (lower.includes(w)) score++;
    });
    negativeWords.forEach((w) => {
      if (lower.includes(w)) score--;
    });

    if (score > 1) return "Positive 😊";
    if (score < -1) return "Negative 😔";
    return "Neutral 😐";
  };

  useEffect(() => {
    if (entry.trim().length > 0) {
      setSentiment(analyzeSentiment(entry));
    } else {
      setSentiment("Neutral");
    }
  }, [entry]);

  // ✍️ Save Entry
  const saveEntry = () => {
    if (entry.trim() === "") return;
    const today = new Date();
    const todayStr = today.toISOString().split("T")[0];

    const newEntry = {
      id: Date.now(),
      text: entry.trim(),
      mood,
      sentiment,
      date: todayStr,
      time: today.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const updated = [newEntry, ...entries];
    setEntries(updated);
    localStorage.setItem("ecoJournalEntries", JSON.stringify(updated));
    setEntry("");
    setMood("");
    setSentiment("Neutral");
    updateStreak(todayStr); // ⭐ Calls streak update each save
  };

  // 🔥 Update streak logic (improved + popup)
  const updateStreak = (todayStr) => {
    if (!lastDate) {
      setStreak(1);
      setLastDate(todayStr);
      localStorage.setItem("ecoJournalStreak", "1");
      localStorage.setItem("ecoJournalLastDate", todayStr);
      showStreakPopup(1); // ⭐ show popup
      return;
    }

    const last = new Date(lastDate);
    const today = new Date(todayStr);
    const diffDays = Math.floor((today - last) / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      const newStreak = streak + 1;
      setStreak(newStreak);
      setLastDate(todayStr);
      localStorage.setItem("ecoJournalStreak", newStreak.toString());
      localStorage.setItem("ecoJournalLastDate", todayStr);
      showStreakPopup(newStreak); // ⭐ popup when streak increases
    } else if (diffDays > 1) {
      // Skipped one or more days → reset to 1
      setStreak(1);
      setLastDate(todayStr);
      localStorage.setItem("ecoJournalStreak", "1");
      localStorage.setItem("ecoJournalLastDate", todayStr);
      showStreakPopup(1); // ⭐ show reset popup
    } else {
      // Same day — no change
      setLastDate(todayStr);
      localStorage.setItem("ecoJournalLastDate", todayStr);
    }
  };

  // ⭐ Streak popup handler
  const showStreakPopup = (count) => {
    setShowPopup(true);
    setTimeout(() => setShowPopup(false), 2500);
  };

  // ❌ Delete Entry
  const deleteEntry = (id) => {
    const updated = entries.filter((e) => e.id !== id);
    setEntries(updated);
    localStorage.setItem("ecoJournalEntries", JSON.stringify(updated));
  };

  // 📊 Insights
  const currentMonth = new Date().toISOString().slice(0, 7);
  const monthlyEntries = entries.filter((e) => e.date.startsWith(currentMonth));
  const moodCounts = moods.map((m) => ({
    mood: m.label,
    emoji: m.emoji,
    count: monthlyEntries.filter((e) => e.mood === m.label).length,
  }));

  const totalEntries = monthlyEntries.length;
  const topMood =
    moodCounts.sort((a, b) => b.count - a.count)[0]?.label || "None";

  return (
    <div className="journal-page">
      <div className="journal-container">
        {/* LEFT SIDE */}
        <div className="journal-left paper">
          <div className="journal-header">
            <h1>🌿 Eco Journal</h1>
            <p>Reflect. Write. Grow Greener Each Day.</p>
            <div className="inspiration-box">💭 <em>{quote}</em></div>
            <div className="streak-box">
              🔥 {streak}-day streak{" "}
              {lastDate && <span>(Last: {lastDate})</span>}
            </div>
          </div>

          <div className="journal-form">
            <textarea
              value={entry}
              onChange={(e) => setEntry(e.target.value)}
              placeholder="Dear Journal, today I..."
            />
            <p className={`sentiment-tag ${sentiment.toLowerCase().split(" ")[0]}`}>
              Sentiment: {sentiment}
            </p>

            <div className="mood-selector">
              {moods.map((m) => (
                <button
                  key={m.label}
                  className={`mood-btn ${mood === m.label ? "selected" : ""}`}
                  onClick={() => setMood(m.label)}
                >
                  {m.emoji}
                </button>
              ))}
            </div>
            <button onClick={saveEntry} className="journal-btn">
              ✍️ Save Entry
            </button>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="journal-right paper">
          <h2 className="section-title">📖 Your Reflections</h2>
          <div className="entries-list">
            {entries.length === 0 ? (
              <p className="empty-text">No entries yet 🌱 Start writing!</p>
            ) : (
              entries.map((e) => (
                <div key={e.id} className="entry-card">
                  <div className="entry-header">
                    <strong>{e.date}</strong>
                    <button onClick={() => deleteEntry(e.id)}>✖</button>
                  </div>
                  <div className="entry-body">
                    {e.mood && (
                      <span className="entry-mood">
                        {moods.find((m) => m.label === e.mood)?.emoji} {e.mood}
                      </span>
                    )}
                    <p>{e.text}</p>
                    <p className="entry-sentiment">
                      💬 {e.sentiment || "Neutral 😐"}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="stats-section">
            <h2>📊 Monthly Insights</h2>
            <p>
              Total entries: <strong>{totalEntries}</strong>
            </p>
            <p>
              Most common mood: <strong>{topMood}</strong>
            </p>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={moodCounts}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="emoji" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#9b7e46" radius={6} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* ⭐ Popup animation */}
      {showPopup && (
        <div className="streak-popup">
          🔥 Streak Updated! You’re on {streak} day{streak > 1 ? "s" : ""}!
        </div>
      )}
    </div>
  );
}
