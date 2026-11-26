# CropIQ

CropIQ is a crop recommendation and historical price-range web application for Indian farmers. It recommends the top 3 suitable crops from weather conditions and any available soil-test values (supporting full, partial, or zero soil data), explains each recommendation in plain language, displays historical 4-month price ranges (and per-acre profit when yield and cost data are supplied), and supports both **English** and **Kannada** (text and browser voice).

---

## Folder Structure

```text
cropiq/
  README.md
  requirements.txt
  backend/
    app/
      main.py                 # FastAPI app, CORS, GET /, POST /recommend
      recommender.py          # Soil-mode selection, top-3 ranking, explanations, bounds validation
      economics.py            # Historical 4-month modal price range & profit engine
      schemas.py              # Pydantic request/response schemas
    data/
      Crop_recommendation.csv # User-supplied Kaggle dataset (2200 rows, 22 crops)
      prices/
        paddy.csv             # User-supplied monthly CEDA Agmarknet modal prices
      crop_economics.csv      # Yield and cultivation cost table (TODO_SOURCE by default)
    models/
      crop_profiles.json      # Generated 5th-95th percentile feature ranges per crop
      mode_models.joblib      # Generated 16 RandomForestClassifier models + CV scores
    scripts/
      check_data.py           # Dataset validation checks
      build_profiles.py       # Generates backend/models/crop_profiles.json
      train_modes.py          # Trains all 16 models and prints CV accuracy table
      price_range_test.py     # Reproduces 4-month range and 12-month coverage check
    tests/
      conftest.py
      test_backend_core.py
      test_economics.py
  frontend/                   # React + Vite (JavaScript, plain CSS)
  docs/
    RESULTS.md
    ARCHITECTURE.md
```

---

## Tested Environment

- **OS:** Windows 11 (PowerShell)
- **Python:** 3.13.1 (`py -m venv .venv`)
- **Node / npm:** Node `v24.19.0`, npm `11.17.0`
- **No paid services or API keys required.**

---

## Setup & Run Commands (Windows PowerShell)

### 1. Backend Setup

Open PowerShell in the `cropiq` root folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Verify the supplied datasets and build the model artifacts:

```powershell
python backend/scripts/check_data.py
python backend/scripts/build_profiles.py
python backend/scripts/train_modes.py
python backend/scripts/price_range_test.py
```

Start the FastAPI backend from the `backend/` folder (`http://127.0.0.1:8000`):

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Frontend Setup (new PowerShell terminal)

From the `cropiq` root folder:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. Run Backend Tests

From `cropiq/backend` (with `.venv` activated):

```powershell
python -m pytest tests\ -v
```

---

## Browser Voice Notes

- Voice input uses the browser's Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) with `en-IN` and `kn-IN`, and always shows parsed numbers for confirmation before applying them to the form.
- Voice output uses `window.speechSynthesis` to read the top recommended crop and its reasons in the selected language.
- **Kannada speech recognition quality varies across devices and browsers; Google Chrome is recommended.** Browsers without Web Speech support hide the voice buttons and display a short fallback note.

---

## Data & Economics Notes

- `backend/data/crop_economics.csv` ships with a `paddy` pilot row containing `TODO_SOURCE` for yield, cost, source, and year. Profit values remain `"data not available"` in the UI until verified figures are added to that CSV.
- To enable price/profit for additional crops later, add `backend/data/prices/<crop>.csv` (`date,modal,min,max`) and a matching row in `backend/data/crop_economics.csv`.
