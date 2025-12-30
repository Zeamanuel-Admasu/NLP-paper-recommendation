import os
import zipfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import numpy as np
import pickle
import torch
import tensorflow as tf
from sentence_transformers import SentenceTransformer, util

# -------------------------
# Config
# -------------------------
# If MODELS_DIR is set, we load from there.
# Otherwise we load from ./models
MODEL_DIR = Path(os.getenv("MODELS_DIR", "models"))

# If models are not present, and MODELS_ZIP_PATH is provided, we extract it.
# (Useful when you download a zip manually / from releases and point to it.)
MODELS_ZIP_PATH: Optional[str] = os.getenv("MODELS_ZIP_PATH")

# Optional: if you want to force-disable transformers' TF usage
# (SentenceTransformer uses PyTorch anyway; this can prevent TF/Keras import issues in some setups.)
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")


# -------------------------
# Helpers for model folder setup
# -------------------------
def ensure_models_present():
    """
    Ensures MODEL_DIR contains:
      - full_model_savedmodel/saved_model.pb + variables/
      - label_vocab.pkl
      - embeddings.pt
      - sentences.pkl

    If not, and MODELS_ZIP_PATH is provided, extract that zip into MODEL_DIR.
    """
    needed_paths = [
        MODEL_DIR / "full_model_savedmodel" / "saved_model.pb",
        MODEL_DIR / "full_model_savedmodel" / "variables" / "variables.index",
        MODEL_DIR / "full_model_savedmodel" / "variables" / "variables.data-00000-of-00001",
        MODEL_DIR / "label_vocab.pkl",
        MODEL_DIR / "embeddings.pt",
        MODEL_DIR / "sentences.pkl",
    ]

    if all(p.exists() for p in needed_paths):
        return

    # Try to extract from zip if provided
    if MODELS_ZIP_PATH:
        zip_path = Path(MODELS_ZIP_PATH)
        if not zip_path.exists():
            raise RuntimeError(
                f"Models are missing and MODELS_ZIP_PATH was set, "
                f"but zip file not found: {zip_path}"
            )

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(MODEL_DIR)

        # Re-check
        if not all(p.exists() for p in needed_paths):
            raise RuntimeError(
                "Extracted models zip but still missing required files. "
                "Check your zip structure."
            )
        return

    # If no zip path, fail with a clear message
    missing = [str(p) for p in needed_paths if not p.exists()]
    raise RuntimeError(
        "Required model files are missing.\n"
        f"MODEL_DIR={MODEL_DIR}\n"
        "Missing:\n- " + "\n- ".join(missing) + "\n\n"
        "Fix options:\n"
        "1) Put the model files into ./models\n"
        "2) Set MODELS_DIR to the folder containing the models\n"
        "3) Set MODELS_ZIP_PATH to a local zip and restart"
    )


# -------------------------
# Request and response models
# -------------------------
class PredictRequest(BaseModel):
    text: str = Field(min_length=5)
    top_k: int = Field(default=5, ge=1, le=30)


class RecommendRequest(BaseModel):
    query: str = Field(min_length=2)
    k: int = Field(default=5, ge=1, le=30)


# -------------------------
# Application setup
# -------------------------
app = FastAPI(title="ArXiv Assistant Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Globals (loaded on startup)
# -------------------------
infer = None
MODEL_INPUT_KEY = None
label_vocab = None
embeddings = None
sentences = None
rec_model = None


# -------------------------
# Load everything once at startup
# -------------------------
@app.on_event("startup")
def startup_load_models():
    global infer, MODEL_INPUT_KEY, label_vocab, embeddings, sentences, rec_model

    ensure_models_present()

    # Subject prediction model (SavedModel)
    loaded = tf.saved_model.load(str(MODEL_DIR / "full_model_savedmodel"))
    infer = loaded.signatures["serving_default"]

    # Detect the correct input key name automatically
    input_keys = list(infer.structured_input_signature[1].keys())
    if not input_keys:
        raise RuntimeError("SavedModel has no input keys in serving_default signature.")
    MODEL_INPUT_KEY = input_keys[0]

    # Label vocabulary
    with open(MODEL_DIR / "label_vocab.pkl", "rb") as f:
        label_vocab = pickle.load(f)

    # Recommendation data
    embeddings = torch.load(MODEL_DIR / "embeddings.pt", map_location="cpu")
    with open(MODEL_DIR / "sentences.pkl", "rb") as f:
        sentences = pickle.load(f)

    # SentenceTransformer (downloads model if not cached)
    rec_model = SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------
# Helper functions
# -------------------------
def predict_top_k_subjects(text: str, top_k: int):
    if infer is None or MODEL_INPUT_KEY is None or label_vocab is None:
        raise HTTPException(status_code=503, detail="Models not loaded yet.")

    out = infer(**{MODEL_INPUT_KEY: tf.constant([[text]])})

    # Output tensor: probabilities
    probs = list(out.values())[0].numpy()[0]  # shape: (num_labels,)

    top_indices = np.argsort(probs)[::-1][:top_k]
    results = []
    for i in top_indices:
        label = str(label_vocab[i])
        if label != "[UNK]":
            results.append({"label": label, "score": float(probs[i])})
    return results


def recommend_titles(query: str, k: int):
    if rec_model is None or embeddings is None or sentences is None:
        raise HTTPException(status_code=503, detail="Recommendation models not loaded yet.")

    query_embedding = rec_model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, embeddings)[0]  # shape: (N,)
    top_results = torch.topk(cosine_scores, k=k)

    results = []
    for idx, score in zip(top_results.indices.tolist(), top_results.values.tolist()):
        results.append({"title": sentences[idx], "score": float(score)})
    return results


# -------------------------
# Endpoints
# -------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_dir": str(MODEL_DIR),
        "saved_model_exists": (MODEL_DIR / "full_model_savedmodel" / "saved_model.pb").exists(),
        "embeddings_exists": (MODEL_DIR / "embeddings.pt").exists(),
        "sentences_exists": (MODEL_DIR / "sentences.pkl").exists(),
        "label_vocab_exists": (MODEL_DIR / "label_vocab.pkl").exists(),
    }


@app.post("/predict-subjects")
def predict_subjects(req: PredictRequest):
    return {"predictions": predict_top_k_subjects(req.text, req.top_k)}


@app.post("/recommend")
def recommend(req: RecommendRequest):
    return {"recommendations": recommend_titles(req.query, req.k)}
