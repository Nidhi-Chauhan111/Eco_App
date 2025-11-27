// src/EcoSuggestions.js
import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import "./App.css";

/* fallback tips (only used when server returns nothing / error) */
const fallbackTips = [
  "Reduce, reuse, recycle ",
  "Go for a meat-free Monday ",
  "Try public transport twice a week ",
  "Switch off unused appliances to save energy ",
  "Conserve water — shorter showers ",
  "Plant a tree "
];

function shuffle(arr) {
  return arr.slice().sort(() => Math.random() - 0.5);
}

/**
 * Props:
 *  - propPayload (optional) : payload passed from nav state or parent
 *  - recommendationsApi (optional) : relative path on backend (default "/calculator/recommendations")
 *
 * IMPORTANT: this component expects your backend to be reachable at
 * `RECOMMENDATIONS_BACKEND + recommendationsApi`. Adjust RECOMMENDATIONS_BACKEND below.
 */
export default function EcoSuggestions({
  propPayload = null,
  recommendationsApi = "/calculator/recommendations"
}) {
  // change this to your actual backend base (use 127.0.0.1:8000 if that's what your server uses)
  const RECOMMENDATIONS_BACKEND = "http://127.0.0.1:8000";

  const loc = useLocation();
  const [payload, setPayload] = useState(propPayload);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recs, setRecs] = useState(null);
  const [usedFallback, setUsedFallback] = useState(false);

  // Try location.state, then prop, then localStorage for payload
  useEffect(() => {
    if (payload) return;
    const locPayload = loc?.state?.payload ?? null;
    if (locPayload) {
      console.debug("[EcoSuggestions] using payload from location.state", locPayload);
      setPayload(locPayload);
      return;
    }
    if (propPayload) {
      console.debug("[EcoSuggestions] using propPayload", propPayload);
      setPayload(propPayload);
      return;
    }
    try {
      const stored = localStorage.getItem("last_payload");
      if (stored) {
        const parsed = JSON.parse(stored);
        console.debug("[EcoSuggestions] using payload from localStorage", parsed);
        setPayload(parsed);
      }
    } catch (e) {
      console.warn("[EcoSuggestions] localStorage parse error", e);
    }
  }, [loc, propPayload, payload]);

  useEffect(() => {
    async function fetchRecs() {
      // if no payload: do fallback immediately
      if (!payload) {
        console.debug("[EcoSuggestions] no payload available — using fallback tips");
        setRecs(shuffle(fallbackTips));
        setUsedFallback(true);
        return;
      }

      setLoading(true);
      setError(null);
      setUsedFallback(false);

      try {
        const token = localStorage.getItem("access_token") || localStorage.getItem("token") || null;
        const headers = { "Content-Type": "application/json" };
        if (token) headers["Authorization"] = `Bearer ${token}`;

        const url = `${RECOMMENDATIONS_BACKEND}${recommendationsApi}`;
        console.debug("[EcoSuggestions] POSTing to", url, "payload:", payload);

        const res = await fetch(url, {
          method: "POST",
          headers,
          body: JSON.stringify(payload)
        });

        console.debug("[EcoSuggestions] response status", res.status);

        let json = null;
        try {
          json = await res.json();
          console.debug("[EcoSuggestions] response JSON:", json);
        } catch (parseErr) {
          console.error("[EcoSuggestions] Failed to parse response JSON", parseErr);
        }

        // extract recommendations in multiple possible shapes
        let serverRecs = null;

        if (!json) {
          serverRecs = null;
        } else if (Array.isArray(json)) {
          serverRecs = json;
        } else if (Array.isArray(json.recommendations)) {
          // e.g. { recommendations: [ ... ] }
          serverRecs = json.recommendations;
        } else if (json.recommendations && Array.isArray(json.recommendations.recommendations)) {
          // your actual shape: { recommendations: { count: n, recommendations: [ ... ] } }
          serverRecs = json.recommendations.recommendations;
        } else if (json.results && Array.isArray(json.results.recommendations)) {
          serverRecs = json.results.recommendations;
        } else if (json.data && Array.isArray(json.data.recommendations)) {
          serverRecs = json.data.recommendations;
        }

        if (serverRecs && serverRecs.length > 0) {
          console.debug("[EcoSuggestions] Using server recommendations:", serverRecs);
          setRecs(serverRecs);
          setUsedFallback(false);
        } else {
          console.warn("[EcoSuggestions] No server recommendations found — falling back to general tips");
          setRecs(shuffle(fallbackTips));
          setUsedFallback(true);
        }
      } catch (err) {
        console.error("[EcoSuggestions] Error fetching recommendations:", err);
        setError("Could not fetch personalized suggestions — showing general tips.");
        setRecs(shuffle(fallbackTips));
        setUsedFallback(true);
      } finally {
        setLoading(false);
      }
    }

    fetchRecs();
  }, [payload, recommendationsApi]); // run when payload arrives or api path changes

  // Render
  return (
    <div className="suggestion-page" style={{ padding: "24px" }}>
      <h2 className="suggestion-title">🌍 Eco-Friendly Suggestions</h2>
      <p className="suggestion-subtitle">
        Small actions make a big impact — start today!
        {usedFallback && <span style={{ color: "#b33", marginLeft: 8 }}> (showing general tips)</span>}
      </p>

      {loading && <div style={{ textAlign: "center", margin: 18 }}>Loading suggestions…</div>}
      {error && <div style={{ color: "#b33", textAlign: "center", marginBottom: 12 }}>{error}</div>}

      <div className="suggestion-grid" style={{ marginTop: 18 }}>
        {(recs || []).map((tip, idx) => {
          // tip may be a string or object {text:..., title:...}
          const text = typeof tip === "string" ? tip : (tip.text || tip.title || JSON.stringify(tip));
          return (
            <div key={idx} className="suggestion-card" style={{ backgroundColor: "#eef9f1" }}>
              <h3 style={{ margin: "8px 0" }}>{text}</h3>
            </div>
          );
        })}
      </div>

      {/* debug area you can temporarily enable */}
      {/*<div style={{ marginTop: 14, fontSize: 12, color: "#666" }}>
        <div>Debug: payload present? {payload ? "yes" : "no"}</div>
        <div>Debug: recs length: {recs ? recs.length : 0}</div>
      </div>*/}
    </div>
  );
}
