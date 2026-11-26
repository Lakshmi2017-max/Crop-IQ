import { useEffect, useRef, useState } from "react";
import {
  TRANSLATIONS,
  buildTranslatedReason,
  getModeLabel,
  translateCropName,
} from "./i18n/index.js";
import {
  isSpeechRecognitionSupported,
  isSpeechSynthesisSupported,
  parseVoiceTranscript,
  speakText,
  startVoiceRecognition,
  stopSpeaking,
} from "./voice.js";

const API_BASE = "http://127.0.0.1:8000";

const WEATHER_KEYS = ["temperature", "humidity", "rainfall"];
const SOIL_KEYS = ["n", "p", "k", "ph"];
const ALL_FIELD_KEYS = [...WEATHER_KEYS, ...SOIL_KEYS];

const INITIAL_FORM = {
  temperature: "",
  humidity: "",
  rainfall: "",
  n: "",
  p: "",
  k: "",
  ph: "",
};

const SAMPLE_FORM = {
  temperature: "21",
  humidity: "82",
  rainfall: "203",
  n: "90",
  p: "42",
  k: "43",
  ph: "6.5",
};

function formatCurrency(val, fallbackText) {
  if (val === null || val === undefined) {
    return fallbackText;
  }
  return `₹${Number(val).toLocaleString("en-IN", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })}`;
}

function renderFieldError(errObj, t) {
  if (!errObj) {
    return "";
  }
  if (errObj.type === "required") {
    return t.errWeatherRequired;
  }
  if (errObj.type === "invalid") {
    return t.errInvalidNumber;
  }
  if (errObj.type === "range") {
    return t.errOutOfRange(errObj.min, errObj.max);
  }
  if (errObj.type === "api_range") {
    return t.errApiOutOfRange(errObj.min, errObj.max);
  }
  return t.errGenericInvalid;
}

function renderApiError(errObj, t) {
  if (!errObj) {
    return "";
  }
  if (errObj.type === "fix_inputs") {
    return t.apiFixInputs;
  }
  if (errObj.type === "server") {
    return t.apiServerError(errObj.status);
  }
  if (errObj.type === "down") {
    return t.apiDown;
  }
  return "";
}

export default function App() {
  const [lang, setLang] = useState("en");
  const [form, setForm] = useState(INITIAL_FORM);
  const [rankBy, setRankBy] = useState("suitability");
  const [fieldErrors, setFieldErrors] = useState({});
  const [knownBounds, setKnownBounds] = useState({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);
  const [result, setResult] = useState(null);

  // Voice input & speech synthesis states
  const [listening, setListening] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const [pendingVoice, setPendingVoice] = useState(null);
  const [speaking, setSpeaking] = useState(false);
  const recognitionRef = useRef(null);

  const sttSupported = isSpeechRecognitionSupported();
  const ttsSupported = isSpeechSynthesisSupported();
  const t = TRANSLATIONS[lang];

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {
          // ignore cleanup stop errors
        }
      }
      stopSpeaking();
    };
  }, []);

  function handleLanguageSwitch(nextLang) {
    stopSpeaking();
    setSpeaking(false);
    setLang(nextLang);
  }

  function validateSingleField(key, rawValue, boundsMap = knownBounds) {
    const trimmed = String(rawValue).trim();
    const isWeather = WEATHER_KEYS.includes(key);

    if (trimmed === "") {
      return isWeather ? { type: "required" } : null;
    }

    const num = Number(trimmed);
    if (!Number.isFinite(num)) {
      return { type: "invalid" };
    }

    const bounds = boundsMap[key];
    if (bounds && (num < bounds.min || num > bounds.max)) {
      return { type: "range", min: bounds.min, max: bounds.max };
    }
    return null;
  }

  function handleFieldChange(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
    const err = validateSingleField(key, value);
    setFieldErrors((prev) => ({ ...prev, [key]: err }));
  }

  function handleVoiceInputStart() {
    if (!sttSupported) {
      return;
    }
    if (listening && recognitionRef.current) {
      recognitionRef.current.stop();
      setListening(false);
      return;
    }

    setVoiceError(null);
    setPendingVoice(null);
    setListening(true);

    recognitionRef.current = startVoiceRecognition({
      lang,
      onResult: (transcript) => {
        const parsed = parseVoiceTranscript(transcript);
        setPendingVoice({ transcript, parsed });
      },
      onError: (code) => {
        setVoiceError(code);
        setListening(false);
      },
      onEnd: () => {
        setListening(false);
      },
    });
  }

  function confirmVoiceValues() {
    if (!pendingVoice) {
      return;
    }
    const nextForm = { ...form, ...pendingVoice.parsed };
    const nextErrors = { ...fieldErrors };
    for (const key of Object.keys(pendingVoice.parsed)) {
      nextErrors[key] = validateSingleField(key, nextForm[key]);
    }
    setForm(nextForm);
    setFieldErrors(nextErrors);
    setPendingVoice(null);
    setVoiceError(null);
  }

  function discardVoiceValues() {
    setPendingVoice(null);
    setVoiceError(null);
  }

  function handleSpeakTopCrop() {
    if (!ttsSupported || !result || !result.recommendations?.length) {
      return;
    }
    if (speaking) {
      stopSpeaking();
      setSpeaking(false);
      return;
    }

    const top = result.recommendations[0];
    const details = top.reason_details || [];
    const within = details.filter((d) => d.status === "within").length;
    const translatedReasons = details.map((d) =>
      buildTranslatedReason(t, d, top.crop)
    );
    const speech = t.voiceSummarySpeech({
      cropName: translateCropName(t, top.crop),
      votePct: Math.round(top.probability * 100),
      within,
      total: details.length,
      reasons: translatedReasons,
    });

    speakText(speech, lang, {
      onStart: () => setSpeaking(true),
      onEnd: () => setSpeaking(false),
      onError: () => setSpeaking(false),
    });
  }

  function buildPayload(selectedRankBy = rankBy) {
    const parseOpt = (v) => (String(v).trim() === "" ? null : Number(v));
    return {
      temperature: Number(form.temperature),
      humidity: Number(form.humidity),
      rainfall: Number(form.rainfall),
      n: parseOpt(form.n),
      p: parseOpt(form.p),
      k: parseOpt(form.k),
      ph: parseOpt(form.ph),
      rank_by: selectedRankBy,
    };
  }

  async function submitRecommendation(selectedRankBy = rankBy) {
    const localErrors = {};
    for (const key of ALL_FIELD_KEYS) {
      const err = validateSingleField(key, form[key]);
      if (err) {
        localErrors[key] = err;
      }
    }
    setFieldErrors(localErrors);
    if (Object.keys(localErrors).length > 0) {
      return;
    }

    stopSpeaking();
    setSpeaking(false);
    setLoading(true);
    setApiError(null);

    try {
      const response = await fetch(`${API_BASE}/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload(selectedRankBy)),
      });

      if (response.status === 422) {
        const errBody = await response.json();
        const nextFieldErrors = {};
        const nextBounds = { ...knownBounds };

        if (Array.isArray(errBody.detail)) {
          for (const item of errBody.detail) {
            if (item.field) {
              if (item.min !== undefined && item.max !== undefined) {
                nextBounds[item.field] = { min: item.min, max: item.max };
                nextFieldErrors[item.field] = {
                  type: "api_range",
                  min: item.min,
                  max: item.max,
                };
              } else {
                nextFieldErrors[item.field] = { type: "generic" };
              }
            } else if (Array.isArray(item.loc) && item.loc.length > 0) {
              const locField = String(item.loc[item.loc.length - 1]);
              nextFieldErrors[locField] = { type: "generic" };
            }
          }
        }
        setKnownBounds(nextBounds);
        setFieldErrors(nextFieldErrors);
        setApiError({ type: "fix_inputs" });
        return;
      }

      if (!response.ok) {
        setApiError({ type: "server", status: response.status });
        return;
      }

      const data = await response.json();
      setResult(data);
    } catch {
      setApiError({ type: "down" });
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    submitRecommendation(rankBy);
  }

  function handleRankByChange(nextRankBy) {
    setRankBy(nextRankBy);
    const hasAllWeather = WEATHER_KEYS.every((k) => String(form[k]).trim() !== "");
    if (result && hasAllWeather) {
      submitRecommendation(nextRankBy);
    }
  }

  function loadSample() {
    setForm(SAMPLE_FORM);
    setFieldErrors({});
    setApiError(null);
    setPendingVoice(null);
  }

  function resetAll() {
    stopSpeaking();
    setSpeaking(false);
    setForm(INITIAL_FORM);
    setFieldErrors({});
    setApiError(null);
    setResult(null);
    setPendingVoice(null);
    setVoiceError(null);
  }

  const accuracyPct = result ? (result.expected_accuracy * 100).toFixed(1) : null;
  const apiErrorText = renderApiError(apiError, t);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>{t.appTitle}</h1>
          <p>{t.appSubtitle}</p>
        </div>
        <div className="lang-switch" role="group" aria-label="Language toggle">
          <button
            type="button"
            className={`lang-btn ${lang === "en" ? "active" : ""}`}
            onClick={() => handleLanguageSwitch("en")}
          >
            English
          </button>
          <button
            type="button"
            className={`lang-btn ${lang === "kn" ? "active" : ""}`}
            onClick={() => handleLanguageSwitch("kn")}
          >
            ಕನ್ನಡ
          </button>
        </div>
      </header>

      <form className="card" onSubmit={handleSubmit} noValidate>
        <div className="form-sections">
          <section>
            <h2 className="section-title">{t.weatherTitle}</h2>
            <p className="section-hint">{t.weatherHint}</p>
            <div className="field-grid">
              {WEATHER_KEYS.map((key) => {
                const field = t.fields[key];
                const errText = renderFieldError(fieldErrors[key], t);
                return (
                  <div className="field" key={key}>
                    <label htmlFor={`input-${key}`}>
                      {field.label}
                      <span className="required-star">*</span>
                    </label>
                    <input
                      id={`input-${key}`}
                      type="number"
                      step="any"
                      value={form[key]}
                      placeholder={field.placeholder}
                      className={errText ? "input-error" : ""}
                      onChange={(e) => handleFieldChange(key, e.target.value)}
                    />
                    {errText && <span className="field-error">{errText}</span>}
                  </div>
                );
              })}
            </div>
          </section>

          <section>
            <h2 className="section-title">{t.soilTitle}</h2>
            <p className="section-hint">{t.soilHint}</p>
            <div className="field-grid">
              {SOIL_KEYS.map((key) => {
                const field = t.fields[key];
                const errText = renderFieldError(fieldErrors[key], t);
                return (
                  <div className="field" key={key}>
                    <label htmlFor={`input-${key}`}>{field.label}</label>
                    <input
                      id={`input-${key}`}
                      type="number"
                      step="any"
                      value={form[key]}
                      placeholder={field.placeholder}
                      className={errText ? "input-error" : ""}
                      onChange={(e) => handleFieldChange(key, e.target.value)}
                    />
                    {errText && <span className="field-error">{errText}</span>}
                  </div>
                );
              })}
            </div>
          </section>
        </div>

        <div className="voice-bar">
          {sttSupported ? (
            <>
              <button
                type="button"
                className="btn-secondary"
                onClick={handleVoiceInputStart}
              >
                {listening ? t.voiceListeningBtn : t.voiceSpeakBtn}
              </button>
              <p className="voice-hint">{t.voiceHint}</p>
            </>
          ) : (
            <p className="voice-note">{t.voiceUnsupportedInput}</p>
          )}
        </div>

        {voiceError && (
          <div className="status-banner error" role="alert">
            {t.voiceError(voiceError)}
          </div>
        )}

        {pendingVoice && (
          <div className="voice-confirm-box" role="region" aria-label={t.voiceConfirmTitle}>
            <h3>{t.voiceConfirmTitle}</h3>
            <p className="voice-hint">
              <strong>{t.voiceHeardLabel}</strong> {pendingVoice.transcript}
            </p>
            {Object.keys(pendingVoice.parsed).length === 0 ? (
              <p className="field-error">{t.voiceNoNumbers}</p>
            ) : (
              <div className="voice-parsed-grid">
                {ALL_FIELD_KEYS.filter((k) => pendingVoice.parsed[k] !== undefined).map(
                  (key) => (
                    <div className="voice-parsed-chip" key={key}>
                      <span>{t.fields[key].reasonName}</span>
                      <strong>{pendingVoice.parsed[key]}</strong>
                    </div>
                  )
                )}
              </div>
            )}
            <div className="action-buttons">
              {Object.keys(pendingVoice.parsed).length > 0 && (
                <button
                  type="button"
                  className="btn-primary"
                  onClick={confirmVoiceValues}
                >
                  {t.voiceApplyBtn}
                </button>
              )}
              <button
                type="button"
                className="btn-secondary"
                onClick={discardVoiceValues}
              >
                {t.voiceCancelBtn}
              </button>
            </div>
          </div>
        )}

        <div className="form-controls">
          <div className="rank-toggle">
            <span>{t.rankByLabel}</span>
            <div className="toggle-group" role="group" aria-label={t.rankByLabel}>
              <button
                type="button"
                className={`toggle-btn ${rankBy === "suitability" ? "active" : ""}`}
                onClick={() => handleRankByChange("suitability")}
              >
                {t.rankBestMatch}
              </button>
              <button
                type="button"
                className={`toggle-btn ${rankBy === "profit" ? "active" : ""}`}
                onClick={() => handleRankByChange("profit")}
              >
                {t.rankHighestProfit}
              </button>
            </div>
          </div>

          <div className="action-buttons">
            <button type="button" className="btn-secondary" onClick={loadSample}>
              {t.btnSample}
            </button>
            <button type="button" className="btn-secondary" onClick={resetAll}>
              {t.btnClear}
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? t.btnSubmitting : t.btnSubmit}
            </button>
          </div>
        </div>
      </form>

      {apiErrorText && (
        <div className="status-banner error" role="alert">
          {apiErrorText}
        </div>
      )}

      {loading && (
        <div className="status-banner loading" role="status">
          {t.loadingMsg}
        </div>
      )}

      {!loading && !result && !apiErrorText && (
        <div className="card empty-state">
          {t.emptyStatePrefix} <strong>{t.emptyStateAction}</strong>.
        </div>
      )}

      {result && (
        <>
          <div className="status-banner mode mode-banner-row">
            <span>
              {t.modeBanner(
                getModeLabel(t, result.mode, result.soil_values_used),
                accuracyPct
              )}
            </span>
            {ttsSupported ? (
              <button
                type="button"
                className="btn-secondary"
                onClick={handleSpeakTopCrop}
              >
                {speaking ? t.voiceStopResultBtn : t.voiceSpeakResultBtn}
              </button>
            ) : (
              <span className="voice-note">{t.voiceUnsupportedOutput}</span>
            )}
          </div>

          {rankBy === "profit" &&
            result.excluded_from_profit_ranking &&
            result.excluded_from_profit_ranking.length > 0 && (
              <div className="status-banner warn">
                {t.excludedProfitMsg(
                  result.excluded_from_profit_ranking
                    .map((c) => translateCropName(t, c))
                    .join(", ")
                )}
              </div>
            )}

          <div className="cards-grid">
            {result.recommendations.map((rec, index) => {
              const votePct = Math.round(rec.probability * 100);
              const econ = rec.economics;
              const details = rec.reason_details || [];
              const withinCount = details.filter((d) => d.status === "within").length;
              const cropLabel = translateCropName(t, rec.crop);

              return (
                <article className="crop-card" key={rec.crop}>
                  <div className="crop-card-header">
                    <h3 className="crop-name">{cropLabel}</h3>
                    <span className="rank-badge">#{index + 1}</span>
                  </div>

                  <div className="confidence-block">
                    <div className="confidence-label">
                      <span>{t.modelVoteShare}</span>
                      <strong>{votePct}%</strong>
                    </div>
                    <div className="progress-track" aria-hidden="true">
                      <div
                        className="progress-fill"
                        style={{ width: `${Math.max(4, votePct)}%` }}
                      />
                    </div>
                  </div>

                  <span className="conditions-pill">
                    {t.conditionsInRange(withinCount, details.length)}
                  </span>

                  <ul className="reasons-list">
                    {details.map((detail) => {
                      const isWithin = detail.status === "within";
                      return (
                        <li
                          key={detail.feature}
                          className={`reason-item ${
                            isWithin ? "reason-within" : "reason-outside"
                          }`}
                        >
                          {buildTranslatedReason(t, detail, rec.crop)}
                        </li>
                      );
                    })}
                  </ul>

                  <div className="economics-box">
                    <h4>{t.economicsTitle}</h4>
                    {!econ ? (
                      <p>{t.dataNotAvailable}</p>
                    ) : (
                      <>
                        <table className="econ-table">
                          <thead>
                            <tr>
                              <th>{t.econColMetric}</th>
                              <th>{t.econColLow}</th>
                              <th>{t.econColExpected}</th>
                              <th>{t.econColHigh}</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td>{t.econRowPrice}</td>
                              <td>{formatCurrency(econ.price_low, t.dataNotAvailable)}</td>
                              <td>
                                {formatCurrency(econ.price_expected, t.dataNotAvailable)}
                              </td>
                              <td>{formatCurrency(econ.price_high, t.dataNotAvailable)}</td>
                            </tr>
                            <tr>
                              <td>{t.econRowProfit}</td>
                              {econ.profit_expected === null ? (
                                <td colSpan={3}>{t.dataNotAvailable}</td>
                              ) : (
                                <>
                                  <td>
                                    {formatCurrency(econ.profit_low, t.dataNotAvailable)}
                                  </td>
                                  <td>
                                    {formatCurrency(
                                      econ.profit_expected,
                                      t.dataNotAvailable
                                    )}
                                  </td>
                                  <td>
                                    {formatCurrency(econ.profit_high, t.dataNotAvailable)}
                                  </td>
                                </>
                              )}
                            </tr>
                          </tbody>
                        </table>
                        <p className="econ-note">
                          {t.econNote(econ.price_months_of_history)}
                        </p>
                      </>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        </>
      )}

      <section className="card explain-panel">
        <h3>{t.howTitle}</h3>
        <ul>
          {t.howBullets.map((item) => (
            <li key={item.heading}>
              <strong>{item.heading}</strong> {item.body}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
