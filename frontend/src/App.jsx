import { useMemo, useState } from "react";
import "./App.css";
import SubjectPrediction from "./components/SubjectPrediction";
import Recommendations from "./components/Recommendations";
import { getBaseUrl } from "./api";

function TabButton({ active, onClick, children }) {
  return (
    <button
      className={`tabBtn ${active ? "active" : ""}`}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
}

export default function App() {
  const [tab, setTab] = useState("recommend");
  const baseUrl = useMemo(() => getBaseUrl(), []);

  return (
    <div className="page">
      <div className="topBar">
        <div className="brand">
          <div className="logoMark" aria-hidden="true">A</div>
          <div>
            <div className="brandTitle">Research Paper Subject Predictor & Recommender</div>
            <div className="brandSubtitle">
              Predict subject labels and recommend similar titles.
            </div>
          </div>
        </div>

        <div className="tabs">
          <TabButton active={tab === "recommend"} onClick={() => setTab("recommend")}>
            Recommend papers
          </TabButton>
          <TabButton active={tab === "predict"} onClick={() => setTab("predict")}>
            Predict subjects
          </TabButton>
        </div>
      </div>

      <div className="container">
        <div className="grid">
          {tab === "recommend" ? <Recommendations /> : <SubjectPrediction />}
          <div className="sideCard">
            <h3 className="sideTitle">Backend</h3>
            <div className="sideBody">
              <div className="kv">
                <span className="k">Base address</span>
                <span className="v mono">{baseUrl}</span>
              </div>
              <div className="kv">
                <span className="k">Endpoints</span>
                <span className="v mono">/predict-subjects · /recommend</span>
              </div>
              <div className="kv">
                <span className="k">Docs</span>
                <span className="v mono">/docs</span>
              </div>
              <div className="note">
                Tip: if you deploy later, only change <span className="mono">VITE_BACKEND_URL</span>.
              </div>
            </div>
          </div>
        </div>

        <footer className="footer">
          <span className="muted">
            2026 © SITE, AAU
          </span>
        </footer>
      </div>
    </div>
  );
}
