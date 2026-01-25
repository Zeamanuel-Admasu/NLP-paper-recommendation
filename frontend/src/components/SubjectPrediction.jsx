import { useMemo, useState } from "react";
import { predictSubjects } from "../api";

function clampPercent(x) {
  const v = Number(x);
  if (Number.isNaN(v)) return 0;
  return Math.max(0, Math.min(100, Math.round(v)));
}

export default function SubjectPrediction() {
  const [text, setText] = useState(
    "We propose a transformer-based method for question answering."
  );
  const [topK, setTopK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [predictions, setPredictions] = useState([]);

  const disabled = useMemo(() => loading || text.trim().length < 5, [loading, text]);

  async function onPredict() {
    setError("");
    setLoading(true);
    setPredictions([]);
    try {
      const data = await predictSubjects(text, topK);
      setPredictions(data?.predictions || []);
    } catch (e) {
      setError(e?.message || "Failed to predict subjects.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <div className="cardHeader">
        <div>
          <h2 className="cardTitle">Subject prediction</h2>
          <p className="cardSubtitle">
            Paste an abstract (or a short description). The system returns the most likely arXiv
            subject labels.
          </p>
        </div>
      </div>

      <div className="formGrid">
        <div className="field">
          <label className="label">Text</label>
          <textarea
            className="textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste an abstract..."
            rows={7}
          />
          <div className="hint">Minimum 5 characters.</div>
        </div>

        <div className="row">
          <div className="field" style={{ maxWidth: 220 }}>
            <label className="label">Top K</label>
            <input
              className="input"
              type="number"
              min={1}
              max={30}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
            />
          </div>

          <button className="button primary" onClick={onPredict} disabled={disabled}>
            {loading ? "Predicting..." : "Predict"}
          </button>
        </div>

        {error ? (
          <div className="alert error">
            <div className="alertTitle">Error</div>
            <div className="alertBody">{error}</div>
          </div>
        ) : null}
      </div>

      <div className="results">
        {loading ? (
          <div className="skeletonList">
            {Array.from({ length: Math.min(topK, 5) }).map((_, i) => (
              <div className="skeletonRow" key={i} />
            ))}
          </div>
        ) : predictions.length === 0 ? (
          <div className="emptyState">
            No results yet. Click <b>Predict</b>.
          </div>
        ) : (
          <div className="resultList">
            {predictions.map((p, idx) => {
              const percent = clampPercent((p.score || 0) * 100);
              return (
                <div className="resultItem" key={`${p.label}-${idx}`}>
                  <div className="resultTop">
                    <div className="pill">{p.label}</div>
                    <div className="score">
                      <span className="mono">{(p.score ?? 0).toFixed(4)}</span>
                      <span className="muted"> · </span>
                      <span>{percent}%</span>
                    </div>
                  </div>
                  <div className="bar">
                    <div className="barFill" style={{ width: `${percent}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
    