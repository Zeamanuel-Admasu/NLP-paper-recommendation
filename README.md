# NLP-paper-recommendation

A backend service that:
- Predicts arXiv subject areas from an input text
- Recommends paper titles using sentence-embedding similarity

---

## Local Setup (Backend)

### 1) Clone the repository
```bash
git clone https://github.com/Zeamanuel-Admasu/NLP-paper-recommendation.git
cd NLP-paper-recommendation
```

---

### 2) Create and activate a virtual environment (Recommended)
Do not install packages globally. Use a virtual environment to avoid dependency conflicts.

#### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

#### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

---

### 3) Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

---

### 4) Download the model files (Required)
This project loads trained model artifacts (SavedModel + embeddings). Download them from the GitHub Release and extract them into `backend/models/`.

#### Option A: Using the provided script (Recommended)
```bash
python scripts/download_models.py
```

#### Option B: Manual download
1. Download `models.zip` from the repository **Releases** (Models Release).
2. Extract it into:
   - `backend/models/`

After extraction, your folder structure should look like this:

```text
backend/
  models/
    full_model_savedmodel/
      saved_model.pb
      variables/
        variables.index
        variables.data-00000-of-00001
    embeddings.pt
    sentences.pkl
    label_vocab.pkl
```

---

### 5) Run the backend server
From inside the `backend/` folder:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- http://127.0.0.1:8000

Health check:
- http://127.0.0.1:8000/health

Swagger UI:
- http://127.0.0.1:8000/docs
