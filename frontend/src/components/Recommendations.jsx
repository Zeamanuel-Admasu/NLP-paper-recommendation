import { useMemo, useState } from "react";
import { recommendTitles } from "../api";

export default function Recommendations() {
  const [query, setQuery] = useState("transformer question answering");
  const [k, setK] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [recs, setRecs] = useState([]);

  const disabled = useMemo(() => loading || query.trim().length < 2, [loading, query]);

  async function onRecommend() {
    setError("");
    setLoading(true);
    setRecs([]);
    try {
      const data = await recommendTitles(query, k);
      setRecs(data?.recommendations || []);
    } catch (e) {
      setError(e?.message || "Failed to recommend papers.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <div className="cardHeader">
        <div>
          <h2 className="cardTitle">Recommend papers</h2>
          <p className="cardSubtitle">
            Find similar titles using sentence embeddings (cosine similarity).
          </p>
        </div>
      </div>

      <div className="formGrid">
        <div className="field">
          <label className="label">Query</label>
          <input
            className="input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: graph neural networks for recommendation"
          />
          <div className="hint">Minimum 2 characters.</div>
        </div>

        <div className="row">
          <div className="field" style={{ maxWidth: 220 }}>
            <label className="label">Top K</label>
            <input
              className="input"
              type="number"
              min={1}
              max={30}
              value={k}
              onChange={(e) => setK(Number(e.target.value))}
            />
          </div>

          <button className="button primary" onClick={onRecommend} disabled={disabled}>
            {loading ? "Searching..." : "Recommend"}
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
            {Array.from({ length: Math.min(k, 6) }).map((_, i) => (
              <div className="skeletonRow" key={i} />
            ))}
          </div>
        ) : recs.length === 0 ? (
          <div className="emptyState">
            No recommendations yet. Click <b>Recommend</b>.
          </div>
        ) : (
          <ol className="rankedList">
            {recs.map((r, idx) => (
              <li className="rankedItem" key={`${idx}-${r.title?.slice(0, 20)}`}>
                <div className="rankedTitle">{r.title}</div>
                <div className="rankedMeta">
                  Similarity: <span className="mono">{Number(r.score ?? 0).toFixed(4)}</span>
                </div>
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  );
}
