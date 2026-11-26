# CropIQ — System Architecture

CropIQ is organized into seven clean layers with zero paid APIs, zero external databases, and zero hardcoded metrics.

```text
+-------------------------------------------------------------------------+
| 1. UI & Voice Layer (React + Vite: App.jsx, i18n/{en,kn}.js, voice.js)  |
+------------------------------------+------------------------------------+
                                     | HTTP JSON (POST /recommend)
                                     v
+-------------------------------------------------------------------------+
| 2. API & Validation Layer (FastAPI: main.py, schemas.py, recommender.py)|
|    - Required weather (temperature, humidity, rainfall)                 |
|    - Optional soil (n, p, k, ph)                                        |
|    - Dataset min/max bounds widened by 10% -> HTTP 422 with min/max     |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 3. Soil-Mode Selection Layer (recommender.py: select_model_key)         |
|    - Fixed soil order [N, P, K, ph] -> 16 keys ("none" .. "N+P+K+ph")   |
|    - Maps count to Mode A (4), Mode B (1-3), or Mode C (0)              |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 4. ML + Rules Explanation Layer (recommender.py)                        |
|    - RandomForestClassifier predict_proba -> top 3 crops (vote share)   |
|    - crop_profiles.json (5th-95th percentiles) -> reasons & details     |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 5. Profit & Price Engine (economics.py)                                 |
|    - 4-month historical log-return range from MODAL prices only         |
|    - yield * price - cost (null profit if TODO_SOURCE; null if missing) |
|    - rank_by="profit" + excluded_from_profit_ranking                    |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| 6. Storage Layer (File-based: backend/data/ & backend/models/)          |
|    - Crop_recommendation.csv, prices/<crop>.csv, crop_economics.csv     |
|    - mode_models.joblib, crop_profiles.json                             |
+-------------------------------------------------------------------------+
```

---

## Layer-by-Layer Details

### 1. Input Layer (`frontend/src/App.jsx`, `frontend/src/voice.js`)
- Weather inputs (`temperature`, `humidity`, `rainfall`) are required; soil inputs (`n`, `p`, `k`, `ph`) are optional (`step="any"`).
- A `rank_by` toggle switches between `"suitability"` (Best match) and `"profit"` (Highest profit).
- Browser Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) supports `en-IN` and `kn-IN`. `parseVoiceTranscript` normalizes Kannada/ASCII digits, matches labeled or positional numbers, and always presents a confirmation box before updating form inputs.

### 2. Validation Layer (`backend/app/schemas.py`, `backend/app/recommender.py`, `backend/app/main.py`)
- `RecommendRequest` enforces required numeric weather fields and rejects `NaN`/`Inf`.
- At startup (`lifespan` in `main.py`), `compute_feature_bounds` reads `backend/data/Crop_recommendation.csv` and widens each feature's `[min, max]` by `10%` of its span (clamping non-negative features at `0.0`).
- Out-of-range inputs return HTTP `422` containing `{field, feature, value, min, max, msg}`. The React form captures `min`/`max` from API errors for inline validation on subsequent edits.

### 3. Soil-Mode Selection Layer (`backend/app/recommender.py`)
- `select_model_key` checks `N`, `P`, `K`, `ph` in fixed order:
  - 4 provided → `Mode A (full soil data)`, key `"N+P+K+ph"`
  - 1–3 provided → `Mode B (partial soil data)`, key e.g. `"N+K"` or `"P+K+ph"`
  - 0 provided → `Mode C (no soil data)`, key `"none"`
- The selected entry from `mode_models.joblib` supplies the trained classifier, its exact feature column list, and its 5-fold StratifiedKFold `cv_accuracy` returned as `expected_accuracy`.

### 4. ML + Rules Layer (`backend/scripts/train_modes.py`, `build_profiles.py`, `recommender.py`)
- **ML ranking:** Builds a 1-row `pandas.DataFrame` in the model's exact feature order and reads `predict_proba` (the fraction of 100 trees voting for each class) to pick the top 3 crops.
- **Rules-based explanation:** Compares each provided input against the crop's `[5th, 95th]` percentile range stored in `backend/models/crop_profiles.json`, returning `conditions_in_range` (`"X of Y"`), English `reasons`, and structured `reason_details` (`[{feature, value, low, high, status}]`).

### 5. Profit & Price Engine (`backend/app/economics.py`)
- Resolves crop aliases (`rice` → `paddy`) and checks `backend/data/prices/<crop>.csv` plus `backend/data/crop_economics.csv`.
- Computes 4-month log returns `c_t = ln(modal[t+4] / modal[t])` over all available history using the `modal` column only (`min`/`max` are ignored).
- Returns `price_low = latest * exp(q05)`, `price_expected = latest`, `price_high = latest * exp(q95)`.
- Computes `profit = yield * price - cost` for low/expected/high when numeric `yield_quintal_per_acre` and `cost_rs_per_acre` are present; leaves profit fields `null` when marked `TODO_SOURCE`, and returns `economics: null` when either CSV/row is missing.
- When `rank_by="profit"`, crops with numeric `profit_expected` are sorted descending and crops lacking profit data are listed in `excluded_from_profit_ranking`.

### 6. Storage Layer (`backend/data/`, `backend/models/`)
- Raw datasets: `Crop_recommendation.csv`, `prices/paddy.csv` (extensible to any `<crop>.csv`), and `crop_economics.csv`.
- Generated artifacts: `mode_models.joblib` (16 Random Forest models) and `crop_profiles.json` (22 crop percentile profiles).

### 7. UI & Translation Layer (`frontend/src/App.jsx`, `i18n/{en,kn}.js`, `i18n/index.js`, `styles.css`)
- Single-page mobile-friendly green theme (`#2e6b34` primary, `#f3f7f2` background).
- Language toggle switches all UI text, crop names, mode banners, error messages, and reason sentences (reconstructed from `reason_details`) between English and Kannada.
- `window.speechSynthesis` reads the top recommended crop and its translated reasons aloud in the active language.
