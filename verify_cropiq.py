"""
CropIQ one-shot check. Run while the backend is running on port 8000.

From the cropiq folder:
    .venv\\Scripts\\python.exe verify_cropiq.py
Or pass the project folder:
    .venv\\Scripts\\python.exe verify_cropiq.py C:\\path\\to\\cropiq
"""
import json
import os
import sys
import urllib.request
import urllib.error

import numpy as np
import pandas as pd

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
API = "http://127.0.0.1:8000"
PRICES = os.path.join(ROOT, "backend", "data", "prices")
ECON = os.path.join(ROOT, "backend", "data", "crop_economics.csv")

CROPS = ["rice", "maize", "chickpea", "kidneybeans", "pigeonpeas", "mothbeans",
         "mungbean", "blackgram", "lentil", "pomegranate", "banana", "mango",
         "grapes", "watermelon", "muskmelon", "apple", "orange", "papaya",
         "coconut", "cotton", "jute", "coffee"]

passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}  {detail}")


def info(text):
    print(f"  info  {text}")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return 0, str(e)


WEATHER = {"temperature": 21, "humidity": 82, "rainfall": 203}
SOIL = {"n": 90, "p": 42, "k": 43, "ph": 6.5}

print("\n1. API and the three modes")
code, body = call("GET", "/")
check("GET / answers 200", code == 200, f"(got {code}: {body})")
if code != 200:
    print("\nBackend is not reachable. Start it first, then rerun.")
    sys.exit(1)

code, a = call("POST", "/recommend", {**WEATHER, **SOIL})
check("Mode A returns 200", code == 200, f"(got {code})")
if code == 200:
    check("Mode A label", a["mode"].startswith("A"), a["mode"])
    check("Mode A: rice is first", a["recommendations"][0]["crop"] == "rice",
          a["recommendations"][0]["crop"])
    check("Mode A accuracy about 99.5%", 0.99 <= a["expected_accuracy"] <= 1.0,
          a["expected_accuracy"])
    check("Top 3 returned", len(a["recommendations"]) == 3)
    r0 = a["recommendations"][0]
    for key in ("probability", "conditions_in_range", "reasons",
                "reason_details", "economics"):
        check(f"Recommendation has '{key}'", key in r0)

code, b = call("POST", "/recommend", {**WEATHER, "k": 43})
check("Mode B (only K) works", code == 200 and b["mode"].startswith("B"))
if code == 200:
    check("Mode B accuracy about 97.8%", 0.97 <= b["expected_accuracy"] <= 0.99,
          b["expected_accuracy"])

code, c = call("POST", "/recommend", WEATHER)
check("Mode C (no soil) works", code == 200 and c["mode"].startswith("C"))
if code == 200:
    check("Mode C accuracy about 91.9%", 0.90 <= c["expected_accuracy"] <= 0.935,
          c["expected_accuracy"])

print("\n2. Input validation")
code, _ = call("POST", "/recommend", {"humidity": 82, "rainfall": 203})
check("Missing temperature gives 422", code == 422, f"(got {code})")
code, _ = call("POST", "/recommend", {**WEATHER, "temperature": 500})
check("Temperature 500 gives 422", code == 422, f"(got {code})")
code, _ = call("POST", "/recommend", {**WEATHER, "ph": 30})
check("pH 30 gives 422", code == 422, f"(got {code})")

print("\n3. Price files")
if not os.path.isdir(PRICES):
    check("prices folder exists", False, PRICES)
else:
    files = sorted(f for f in os.listdir(PRICES) if f.endswith(".csv"))
    info(f"{len(files)} price files found: {', '.join(files)}")
    check("paddy.csv present", "paddy.csv" in files)
    for f in files:
        name = f[:-4]
        df = pd.read_csv(os.path.join(PRICES, f), parse_dates=["date"])
        s = df.set_index("date")["modal"]
        pairs = sum(1 for t in s.index if t + pd.DateOffset(months=4) in s.index)
        in_model = name in CROPS or name == "paddy"
        enough = len(df) >= 36 and pairs >= 30
        note = []
        if not in_model:
            note.append("NOT one of the 22 crops, unused")
        if not enough:
            note.append("below minimum (36 months, 30 pairs): range should be hidden")
        info(f"{name:12s} {len(df):3d} months, {pairs:3d} pairs  " + "; ".join(note))

    pf = os.path.join(PRICES, "paddy.csv")
    if os.path.exists(pf):
        df = pd.read_csv(pf, parse_dates=["date"]).sort_values("date")
        s = df.set_index("date")["modal"]
        ch = [np.log(s[t + pd.DateOffset(months=4)] / s[t])
              for t in s.index if t + pd.DateOffset(months=4) in s.index]
        now = s.iloc[-1]
        lo = now * np.exp(np.quantile(ch, 0.05))
        hi = now * np.exp(np.quantile(ch, 0.95))
        info(f"paddy range from your file: Rs {lo:.0f} to Rs {hi:.0f} (latest Rs {now:.0f})")
        check("paddy range near Rs 2035 to 2629",
              abs(lo - 2035) / 2035 < 0.05 and abs(hi - 2629) / 2629 < 0.05)

print("\n4. Economics (yield and cost)")
if not os.path.exists(ECON):
    check("crop_economics.csv exists", False, ECON)
else:
    e = pd.read_csv(ECON, dtype=str).fillna("")
    check("22 crop rows", len(e) == 22, f"(found {len(e)})")
    done = e[(e["yield_quintal_per_acre"] != "TODO_SOURCE") &
             (e["cost_rs_per_acre"] != "TODO_SOURCE")]
    info(f"{len(done)} of {len(e)} crops have yield and cost filled in")
    for _, row in done.iterrows():
        check(f"{row['crop']}: has a source",
              row["source"] not in ("", "TODO_SOURCE"),
              "(numbers with no source: do not keep)")

print("\n5. Profit ranking")
code, p = call("POST", "/recommend", {**WEATHER, **SOIL, "rank_by": "profit"})
check("rank_by=profit returns 200", code == 200, f"(got {code})")
if code == 200:
    info("excluded from profit ranking: " +
         str(p.get("excluded_from_profit_ranking")))
    for r in p["recommendations"]:
        eco = r.get("economics")
        if eco is not None:
            info(f"{r['crop']} economics: {json.dumps(eco)}")

print(f"\nResult: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
