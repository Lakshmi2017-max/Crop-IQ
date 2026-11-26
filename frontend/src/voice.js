/**
 * Browser-only Web Speech API helpers (recognition + speechSynthesis) for CropIQ.
 */

const KANNADA_DIGITS = {
  "೦": "0",
  "೧": "1",
  "೨": "2",
  "೩": "3",
  "೪": "4",
  "೫": "5",
  "೬": "6",
  "೭": "7",
  "೮": "8",
  "೯": "9",
};

const FIELD_ORDER = ["temperature", "humidity", "rainfall", "n", "p", "k", "ph"];

const FIELD_PATTERNS = [
  { key: "temperature", pattern: /(?:temperature|temp|ಉಷ್ಣಾಂಶ|ತಾಪಮಾನ)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
  { key: "humidity", pattern: /(?:humidity|ಆರ್ದ್ರತೆ|ತೇವಾಂಶ)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
  { key: "rainfall", pattern: /(?:rainfall|rain|ಮಳೆ)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
  { key: "n", pattern: /(?:nitrogen|\bn\b|ಸಾರಜನಕ)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
  { key: "p", pattern: /(?:phosphorus|phosphorous|\bp\b|ರಂಜಕ)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
  { key: "k", pattern: /(?:potassium|\bk\b|ಪೊಟ್ಯಾಸಿಯಮ್|ಪೊಟ್ಯಾಷ್)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
  { key: "ph", pattern: /(?:soil\s*ph|\bp\s*h\b|\bph\b|ಮಣ್ಣಿನ\s*ಪಿಎಚ್|ಪಿ\s*ಎಚ್|ಪಿಎಚ್)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/gi },
];

export function isSpeechRecognitionSupported() {
  return (
    typeof window !== "undefined" &&
    Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  );
}

export function isSpeechSynthesisSupported() {
  return (
    typeof window !== "undefined" &&
    "speechSynthesis" in window &&
    typeof SpeechSynthesisUtterance !== "undefined"
  );
}

export function normalizeDigits(text) {
  return String(text || "").replace(/[೦-೯]/g, (ch) => KANNADA_DIGITS[ch] ?? ch);
}

/**
 * Parse spoken numbers from a voice transcript into CropIQ form fields.
 * Prefers keyword-labeled matches ("temperature 21, humidity 82"), and falls back
 * to positional order [temperature, humidity, rainfall, n, p, k, ph] for bare numbers.
 */
export function parseVoiceTranscript(rawTranscript) {
  const normalized = normalizeDigits(rawTranscript);
  const parsed = {};

  for (const { key, pattern } of FIELD_PATTERNS) {
    pattern.lastIndex = 0;
    const match = pattern.exec(normalized);
    if (match && match[1] !== undefined) {
      const val = Number(match[1]);
      if (Number.isFinite(val)) {
        parsed[key] = String(val);
      }
    }
  }

  if (Object.keys(parsed).length === 0) {
    const bareNumbers = normalized.match(/-?\d+(?:\.\d+)?/g) || [];
    bareNumbers.slice(0, FIELD_ORDER.length).forEach((numStr, idx) => {
      const val = Number(numStr);
      if (Number.isFinite(val)) {
        parsed[FIELD_ORDER[idx]] = String(val);
      }
    });
  }

  return parsed;
}

export function startVoiceRecognition({ lang, onResult, onError, onEnd }) {
  const RecognitionCtor =
    typeof window !== "undefined" &&
    (window.SpeechRecognition || window.webkitSpeechRecognition);
  if (!RecognitionCtor) {
    return null;
  }

  const recognition = new RecognitionCtor();
  recognition.lang = lang === "kn" ? "kn-IN" : "en-IN";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const transcript = event.results?.[0]?.[0]?.transcript || "";
    onResult(transcript);
  };
  recognition.onerror = (event) => {
    onError(event.error || "unknown");
  };
  recognition.onend = () => {
    onEnd();
  };

  recognition.start();
  return recognition;
}

export function speakText(text, lang, { onStart, onEnd, onError } = {}) {
  if (!isSpeechSynthesisSupported()) {
    return false;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  const targetLang = lang === "kn" ? "kn-IN" : "en-IN";
  utterance.lang = targetLang;

  const voices = window.speechSynthesis.getVoices();
  const langPrefix = lang === "kn" ? "kn" : "en";
  const matchingVoice =
    voices.find((v) => v.lang.toLowerCase() === targetLang.toLowerCase()) ||
    voices.find((v) => v.lang.toLowerCase().startsWith(langPrefix));
  if (matchingVoice) {
    utterance.voice = matchingVoice;
  }

  if (onStart) utterance.onstart = onStart;
  if (onEnd) utterance.onend = onEnd;
  if (onError) utterance.onerror = onError;

  window.speechSynthesis.speak(utterance);
  return true;
}

export function stopSpeaking() {
  if (typeof window !== "undefined" && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
}
