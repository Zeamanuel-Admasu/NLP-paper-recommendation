const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";

async function postJson(path, body) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      msg = data?.detail || data?.message || msg;
    } catch {
      // ignore
    }
    throw new Error(msg);
  }

  return res.json();
}

export async function predictSubjects(text, topK) {
  return postJson("/predict-subjects", { text, top_k: topK });
}

export async function recommendTitles(query, k) {
  return postJson("/recommend", { query, k });
}

export function getBaseUrl() {
  return BASE_URL;
}
