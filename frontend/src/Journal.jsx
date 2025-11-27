import React, { useEffect, useState, useRef } from "react";
import "./App.css";

/**
 * Journal component integrated to backend:
 * - POST /journal/entry  (requires Authorization)
 * - GET  /journal/dashboard (requires Authorization)
 * - GET  /journal/entries/{user_id}  (public)
 *
 * API base (default): http://127.0.0.1:8000
 * You can override by setting REACT_APP_API_URL.
 */
const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("access_token") || localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

export default function Journal() {
  const [entryText, setEntryText] = useState("");
  const [entries, setEntries] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [popup, setPopup] = useState(null); // { sentiment, emotion_summary, inspiration }
  const [userId, setUserId] = useState(null);
  const entryRef = useRef();

  // load dashboard (streak + user id + analytics + recommendations)
  async function loadDashboard() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/journal/dashboard`, {
        method: "GET",
        headers: getAuthHeaders(),
      });
      if (!res.ok) {
        const txt = await res.text().catch(() => null);
        throw new Error(txt || `Dashboard fetch failed (${res.status})`);
      }
      const json = await res.json();
      setDashboard(json);
      // user id helpful for entries endpoint (dashboard contains user_id)
      if (json && json.user_id) setUserId(json.user_id);
      // after we have user id, fetch entries
      if (json && json.user_id) {
        loadEntries(json.user_id);
      } else {
        // fallback: try default user id from backend config "1"
        loadEntries(1);
      }
    } catch (err) {
      console.warn("Dashboard load failed:", err);
      setError("Failed to load dashboard. Please check your login / backend.");
      // Still attempt to load entries for default user
      loadEntries(1);
    } finally {
      setLoading(false);
    }
  }

  // load entries for a given user id
  async function loadEntries(id) {
    if (!id) return;
    try {
      const res = await fetch(`${API_BASE}/journal/entries/${id}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        console.warn("Entries fetch failed:", res.status);
        setEntries([]);
        return;
      }
      const json = await res.json();
      // backend returns { success: true, entries: [...] }
      setEntries((json && json.entries) || []);
    } catch (err) {
      console.warn("Could not load entries:", err);
      setEntries([]);
    }
  }

  useEffect(() => {
    // focus textarea on mount
    entryRef.current?.focus();
    loadDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Submit a journal entry
  async function submitEntry() {
    const text = (entryText || "").trim();
    if (!text) return setError("Please write something before saving.");
    setSaving(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/journal/entry`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ content: text }),
      });

      const json = await (res.json().catch(() => null));
      if (!res.ok) {
        console.warn("Journal post failed:", res.status, json);
        setError((json && json.detail) || (json && json.error) || "Failed to save entry");
        // do not early return — still show fallback local save? (we avoid)
        setSaving(false);
        return;
      }

      // Backend returns: success, entry_id, analysis, inspiration, streak, processed_at
      // We'll show popup using analysis + inspiration and update UI locally.
      if (json && json.success) {
        const newEntry = {
          _id: json.entry_id || `local-${Date.now()}`,
          content: text,
          analysis: json.analysis || {},
          inspiration: json.inspiration || "",
          created_at: json.processed_at || new Date().toISOString(),
        };

        // Prepend to entries list and update dashboard state with new streak
        setEntries((prev) => [newEntry, ...prev]);
        if (json.streak) {
          setDashboard((d) => ({ ...(d || {}), streak_status: json.streak }));
        }

        // show popup summarizing sentiment/inspiration
        const popupContent = {
          sentiment: (json.analysis && json.analysis.sentiment && json.analysis.sentiment.label) || "Neutral",
          emotion_summary: (json.analysis && json.analysis.emotion_summary) || "",
          inspiration: json.inspiration || "",
        };
        setPopup(popupContent);
        // clear textarea
        setEntryText("");
        // auto-dismiss popup after 4s
        setTimeout(() => setPopup(null), 4200);
      } else {
        setError("Server did not accept entry.");
      }
    } catch (err) {
      console.warn("Submit entry error:", err);
      setError("Network error while saving entry.");
    } finally {
      setSaving(false);
    }
  }

  // Delete entry locally (frontend only) — backend delete not available in provided routes
  function deleteLocalEntry(id) {
    setEntries((prev) => prev.filter((e) => e._id !== id));
  }

  // small helper for prettified date
  function fmtDate(iso) {
    if (!iso) return "";
    try {
      const d = new Date(iso);
      return d.toLocaleDateString() + " " + d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return iso;
    }
  }

  return (
    <div className="journal-root">
      <div className="journal-main">
        <div className="journal-left card">
          <div className="journal-header">
            <h1>Eco Journal</h1>
            <p className="sub">Reflect. Track your streak. Grow greener.</p>
          </div>

          <div className="journal-form">
            <textarea
              ref={entryRef}
              placeholder="Write about something you did for the environment today, how you felt, or anything on your mind..."
              value={entryText}
              onChange={(e) => setEntryText(e.target.value)}
              maxLength={3000}
            />
            <div className="form-bottom">
              <div className="sentiment-preview muted">
                {entryText.trim().length === 0 ? "Tip: be honest — small actions matter." : `Preview length: ${entryText.length} chars`}
              </div>

              <div className="controls">
                <button
                  className="btn secondary"
                  onClick={() => {
                    setEntryText("");
                    setError(null);
                  }}
                  disabled={saving || entryText.trim().length === 0}
                >
                  Clear
                </button>
                <button className="btn primary" onClick={submitEntry} disabled={saving || entryText.trim().length === 0}>
                  {saving ? "Saving…" : "Save Entry"}
                </button>
              </div>
            </div>

            {error && <div className="error-box">{error}</div>}
          </div>

          {/* Dashboard (streak / badges / quick stats) */}
          <div className="dashboard card light">
            <h3>Streak & Dashboard</h3>
            {loading ? (
              <p className="muted">Loading...</p>
            ) : dashboard && dashboard.streak_status ? (
              <>
                <div className="streak-row">
                  <div className="streak-box">
                    <div className="streak-number">{dashboard.streak_status.current_streak}</div>
                    <div className="streak-label">current streak (days)</div>
                  </div>

                  <div className="streak-meta">
                    <div>Longest: <strong>{dashboard.streak_status.longest_streak}</strong></div>
                    <div>Total entries: <strong>{dashboard.streak_status.total_entries}</strong></div>
                    <div className={`risk ${dashboard.streak_status.streak_at_risk ? "warn" : ""}`}>
                      {dashboard.streak_status.streak_at_risk ? "Streak at risk" : "On track"}
                    </div>
                  </div>
                </div>

                {/* Next milestone */}
                {dashboard.streak_status.next_milestone && (
                  <div className="milestone">
                    <div className="muted">Next: {dashboard.streak_status.next_milestone.name}</div>
                    <div className="progress-row">
                      <div className="progress-bar">
                        <div style={{ width: `${dashboard.streak_status.next_milestone.progress_percentage}%` }} />
                      </div>
                      <div className="muted small">{Math.round(dashboard.streak_status.next_milestone.progress_percentage)}%</div>
                    </div>
                    <div className="muted small">Days to milestone: {dashboard.streak_status.next_milestone.days_remaining}</div>
                  </div>
                )}

                {/* Achievements preview */}
                <div className="achievements">
                  <div className="muted">Badges</div>
                  <div className="badges-row">
                    {(dashboard.streak_status.achievements || []).slice(0,3).map((ach, idx) => (
                      <div key={idx} className="badge">
                        <div className="badge-emoji">{ach.badge}</div>
                        <div className="badge-meta">
                          <div className="badge-name">{ach.achievement_name || ach.name || ach.achievement_name}</div>
                        </div>
                      </div>
                    ))}
                    {(!dashboard.streak_status.achievements || dashboard.streak_status.achievements.length === 0) && (
                      <div className="muted small">No badges yet — keep going!</div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <p className="muted">No dashboard available (login required).</p>
            )}
          </div>
        </div>

        {/* Right column: entries list + insights */}
        <div className="journal-right">
          <div className="card entries">
            <h3>Recent Entries</h3>
            {entries.length === 0 ? (
              <p className="muted">No entries yet. Your saved entries will show here.</p>
            ) : (
              <div className="entries-list">
                {entries.map((e) => (
                  <div key={e._id} className="entry">
                    <div className="entry-head">
                      <div className="entry-date">{fmtDate(e.created_at)}</div>
                      <div className="entry-actions">
                        <button className="mini" onClick={() => deleteLocalEntry(e._id)}>Remove</button>
                      </div>
                    </div>
                    <div className="entry-body">
                      <div className="entry-text">{e.content}</div>
                      <div className="entry-meta muted">
                        Sentiment: <strong>{(e.analysis && e.analysis.sentiment && e.analysis.sentiment.label) || "N/A"}</strong>
                        {e.inspiration ? <> • Inspiration: <em>{e.inspiration}</em></> : null}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card insights">
            <h3>Quick Insights</h3>
            {dashboard ? (
              <>
                <div className="muted">Consistency</div>
                <div className="big">{dashboard.analytics ? `${dashboard.analytics.consistency_rate}%` : "—"}</div>

                <div className="muted">Recommendations</div>
                <ul className="muted small">
                  {(dashboard.recommendations || []).slice(0,5).map((r, i) => <li key={i}>{r}</li>)}
                  {(!dashboard.recommendations || dashboard.recommendations.length === 0) && <li>No recommendations yet.</li>}
                </ul>
              </>
            ) : (
              <p className="muted">Load the dashboard to see insights.</p>
            )}
          </div>
        </div>
      </div>

      {/* Popup for sentiment/inspiration */}
      {popup && (
        <div className="popup">
          <div className="popup-inner">
            <div className="popup-header">
              <strong>Entry saved</strong>
              <span className="popup-close" onClick={() => setPopup(null)}>✖</span>
            </div>
            <div className="popup-body">
              <div className="muted">Sentiment</div>
              <div className="popup-big">{popup.sentiment}</div>
              {popup.emotion_summary && <div className="muted small">{popup.emotion_summary}</div>}
              {popup.inspiration && (
                <>
                  <div className="muted" style={{ marginTop: 8 }}>Inspiration</div>
                  <div className="popup-inspo">{popup.inspiration}</div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
