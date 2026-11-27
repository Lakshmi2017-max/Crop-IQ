# CropIQ

CropIQ is a crop recommendation and historical price-range web application for Indian farmers. From weather conditions and any available soil-test values (full, partial, or none), it recommends the top 3 suitable crops, explains each recommendation in plain language, shows a historical 4-month price range, and shows profit per acre where yield and cost data are available. The interface supports **English** and **Kannada** (text and browser voice).

Built with AI-assisted tools (Antigravity, Claude). Results in this repository were checked by running the included tests and scripts.

---

## Folder Structure

```text
cropiq/
  README.md
  requirements.txt
  verify_cropiq.py            # One-shot check of the running API, price files and economics file
  price_coverage_all.py       # Walk-forward reliability test of the price range for every crop
  backend/
    app/
      main.py                 # FastAPI app, CORS, GET /, POST /recommend
      recommender.py          # Soil-mode selection, top-3 ranking, explanations, bounds validation
      economics.py            # Historical 4-month price range and profit engine
      schemas.py              # Pydantic request/response schemas
    data/
      Crop_recommendation.csv # Kaggle dataset (2200 rows, 22 crops)
      prices/                 # Monthly CEDA Agmarknet modal prices, one file per crop
        paddy.csv             # used for the crop "rice"
        maize.csv, blackgram.csv, pomegranate.csv, banana.csv, mango.csv, grapes.csv,
        watermelon.csv, muskmelon.csv, apple.csv, orange.csv, papaya.csv, coconut.csv,
        cotton.csv
        ragi.csv              # not one of the 22 crops, ignored
      crop_economics.csv      # Yield and cost per crop (TODO_SOURCE where not yet sourced)
    models/
      crop_profiles.json      # Generated: 5th-95th percentile feature ranges per crop
      mode_models.joblib      # Generated: 16 RandomForest models + cross-validation scores
    scripts/
      check_data.py           # Dataset validation checks
      build_profiles.py       # Generates crop_profiles.json
      train_modes.py          # Trains all 16 models and prints the CV accuracy table
      price_range_test.py     # 4-month range and 12-month coverage check (paddy)
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

## Setup & Run (Windows PowerShell)

### 1. Backend setup

Open PowerShell in the `cropiq` root folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Verify the datasets and build the model files:

```powershell
python backend/scripts/check_data.py
python backend/scripts/build_profiles.py
python backend/scripts/train_modes.py
python backend/scripts/price_range_test.py
```

Start the backend from the `backend/` folder (`http://127.0.0.1:8000`):

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Frontend setup (new PowerShell terminal)

From the `cropiq` root folder:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

### 3. Tests and checks

Unit tests, from `cropiq/backend` (virtual environment active):

```powershell
python -m pytest tests\ -v
```

End-to-end check, from `cropiq` with the backend running:

```powershell
.venv\Scripts\python.exe verify_cropiq.py
```

Price-range reliability for every crop, from `cropiq`:

```powershell
.venv\Scripts\python.exe price_coverage_all.py
```

---

## API

`GET /` returns `{"status": "CropIQ API running"}`.

`POST /recommend` takes `temperature`, `humidity` and `rainfall` (required), optional soil values `n`, `p`, `k` and `ph`, and `rank_by` (`"suitability"` or `"profit"`):

```json
{"temperature": 21, "humidity": 82, "rainfall": 203, "n": 90, "p": 42, "k": 43, "ph": 6.5}
```

The response gives the soil mode, the expected accuracy of the model used, and the top 3 crops. Each crop has a vote share, the number of conditions in range, reasons, and an `economics` block (price range and profit, or null). Out-of-range or missing values return HTTP 422.

---

## Results (reproduced by the scripts above)

Random Forest, 5-fold cross-validated accuracy by number of soil values provided:

| Soil values given | Mode | Accuracy |
|---|---|---|
| 4 (N, P, K, pH) | A | about 99.5% |
| 3 | B | 99.1% to 99.45% |
| 2 | B | 97.3% to 98.9% |
| 1 | B | 94.9% to 97.8% |
| 0 (weather only) | C | about 91.9% |

The price range was tested by pretending to stand in past months and checking whether the real price 4 months later fell inside the range. Across 13 crops (12 tests each), the real price landed inside the range in 125 of 156 tests (80%) against a 90% target; paddy scored 9 of 12. The full per-crop table is saved as `price_range_coverage.csv` by `price_coverage_all.py`.

---

## Browser Voice Notes

- Voice input uses the browser's Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) with `en-IN` and `kn-IN`, and always shows parsed numbers for confirmation before applying them to the form.
- Voice output uses `window.speechSynthesis` to read the top recommended crop and its reasons in the selected language.
- **Kannada speech recognition quality varies across devices and browsers; Google Chrome is recommended.** Browsers without Web Speech support hide the voice buttons and show a short fallback note.

---

## Data & Economics Notes

- **Price range:** shown for any crop whose file in `backend/data/prices/` has at least 36 months of data and at least 30 pairs of months 4 apart, matched by calendar date. Otherwise the app shows "data not available" (for example mango, with 35 months). The range is the 5th to 95th percentile of past 4-month changes applied to the latest modal price. It is a typical historical range, not a forecast.
- **Why not a forecast:** on 61 months of paddy prices, Random Forest and Ridge models did not beat a naive "price stays the same" baseline (error 6.8% for naive against 10.6% for the best model).
- **Price files:** `<crop>.csv` with columns `date,modal,min,max`. Only the modal price is used, because min and max are inconsistent in recent months. The crop `rice` uses `paddy.csv`. `ragi.csv` is not one of the 22 crops and is ignored.
- **Profit per acre:** needs a row in `crop_economics.csv` with real yield and cost. Only rice is filled: Karnataka paddy, C2 cost, from the CACP Price Policy for Kharif Crops, Marketing Season 2024-25, Annex Table 5.5 (projected, state average, kharif season). All other rows are `TODO_SOURCE` and show "data not available" in the app. Never enter numbers without a source.
- **Adding a crop:** put `<crop>.csv` in `backend/data/prices/` (the file name must match the crop label) and add a sourced row to `crop_economics.csv` if you want profit as well.

---

## Data Sources

1. Kaggle, "Crop Recommendation Dataset" (2,200 records, 22 crops).
2. Centre for Economic Data and Analysis (CEDA), Ashoka University, "Agri-Market Data": Karnataka monthly mandi prices, Nov 2020 to Oct 2025 (source: Directorate of Marketing & Inspection, Ministry of Agriculture and Farmers Welfare, Government of India).
3. Commission for Agricultural Costs and Prices (CACP), Government of India, "Price Policy for Kharif Crops: The Marketing Season 2024-25".

---

## Known Limitations

- The 99.5% (full soil) and 91.9% (no soil) accuracies are cross-validated results on a benchmark dataset. The dataset's weather values are typical conditions for each crop, so real-farm accuracy will be lower, especially in Mode C.
- Prices are Karnataka mandi prices, including for crops grown mainly elsewhere (for example apple).
- Several crops have missing months in 2024 (banana, grapes, watermelon, muskmelon, papaya), which makes their ranges less reliable.
- The price range was less reliable for coconut, blackgram and papaya in testing (8, 7 and 4 of 12).
- Profit is available only for rice, using a state-average projected cost.
- Tree and vine crops (apple, orange, mango, grapes, coconut, pomegranate, banana, papaya) are perennial, so a single-season profit figure does not describe them well.
- The Kannada text has not yet been reviewed by a native speaker.