// Every Kannada string below is marked NEEDS HUMAN REVIEW for native speaker verification.
const kn = {
  langCode: "kn",
  appTitle: "ಕ್ರಾಪ್‌ಐಕ್ಯೂ", // NEEDS HUMAN REVIEW
  appSubtitle: "ಭಾರತೀಯ ರೈತರಿಗಾಗಿ ಬೆಳೆ ಶಿಫಾರಸು ಮತ್ತು ಐತಿಹಾಸಿಕ ಬೆಲೆ ಶ್ರೇಣಿ", // NEEDS HUMAN REVIEW
  weatherTitle: "ಹವಾಮಾನ ಮಾಹಿತಿ", // NEEDS HUMAN REVIEW
  weatherHint: "ನಿಮ್ಮ ಪ್ರದೇಶ ಮತ್ತು ಹಂಗಾಮಿಗೆ ಅಗತ್ಯವಿರುವ ವಿವರಗಳು.", // NEEDS HUMAN REVIEW
  soilTitle: "ಮಣ್ಣು ಪರೀಕ್ಷೆ ಮೌಲ್ಯಗಳು (ಐಚ್ಛಿಕ)", // NEEDS HUMAN REVIEW
  soilHint: "ನಿಮ್ಮ ಬಳಿ ಇರುವ ಮೌಲ್ಯಗಳನ್ನು ನಮೂದಿಸಿ; ಹೆಚ್ಚು ಮಾಹಿತಿ ನೀಡಿದರೆ ನಿಖರತೆ ಹೆಚ್ಚುತ್ತದೆ", // NEEDS HUMAN REVIEW
  rankByLabel: "ಕ್ರಮಾನುಗತ:", // NEEDS HUMAN REVIEW
  rankBestMatch: "ಉತ್ತಮ ಹೊಂದಾಣಿಕೆ", // NEEDS HUMAN REVIEW
  rankHighestProfit: "ಗರಿಷ್ಠ ಲಾಭ", // NEEDS HUMAN REVIEW
  btnSample: "ಮಾದರಿ ಮೌಲ್ಯಗಳು", // NEEDS HUMAN REVIEW
  btnClear: "ಅಳಿಸಿ", // NEEDS HUMAN REVIEW
  btnSubmit: "ಬೆಳೆ ಶಿಫಾರಸು ಪಡೆಯಿರಿ", // NEEDS HUMAN REVIEW
  btnSubmitting: "ಬೆಳೆಗಳನ್ನು ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ...", // NEEDS HUMAN REVIEW
  voiceSpeakBtn: "ಧ್ವನಿ ಮೂಲಕ ನಮೂದಿಸಿ", // NEEDS HUMAN REVIEW
  voiceListeningBtn: "ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದೆ...", // NEEDS HUMAN REVIEW
  voiceHint:
    "ಉದಾಹರಣೆ: \"ಉಷ್ಣಾಂಶ 21, ಆರ್ದ್ರತೆ 82, ಮಳೆ 203, ಸಾರಜನಕ 90, ರಂಜಕ 42, ಪೊಟ್ಯಾಸಿಯಮ್ 43, ಪಿಎಚ್ 6.5\"", // NEEDS HUMAN REVIEW
  voiceUnsupportedInput:
    "ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ನಮೂದು ಬೆಂಬಲಿತವಾಗಿಲ್ಲ. ಕ್ರೋಮ್ ಬ್ರೌಸರ್ ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.", // NEEDS HUMAN REVIEW
  voiceUnsupportedOutput:
    "ಈ ಬ್ರೌಸರ್‌ನಲ್ಲಿ ಧ್ವನಿ ಓದುವಿಕೆ ಬೆಂಬಲಿತವಾಗಿಲ್ಲ.", // NEEDS HUMAN REVIEW
  voiceConfirmTitle: "ಫಾರ್ಮ್‌ಗೆ ಸೇರಿಸುವ ಮೊದಲು ಧ್ವನಿ ಮೌಲ್ಯಗಳನ್ನು ದೃಢೀಕರಿಸಿ", // NEEDS HUMAN REVIEW
  voiceHeardLabel: "ಕೇಳಿಸಿದ್ದು:", // NEEDS HUMAN REVIEW
  voiceNoNumbers: "ಯಾವುದೇ ಸಂಖ್ಯೆಗಳು ಗುರುತಿಸಲ್ಪಡಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಮಾತನಾಡಿ.", // NEEDS HUMAN REVIEW
  voiceApplyBtn: "ಫಾರ್ಮ್‌ಗೆ ಅನ್ವಯಿಸಿ", // NEEDS HUMAN REVIEW
  voiceCancelBtn: "ರದ್ದುಮಾಡಿ", // NEEDS HUMAN REVIEW
  voiceError: (code) => `ಧ್ವನಿ ದೋಷ (${code}). ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.`, // NEEDS HUMAN REVIEW
  voiceSpeakResultBtn: "ಮೇಲಿನ ಬೆಳೆಯನ್ನು ಓದಿ", // NEEDS HUMAN REVIEW
  voiceStopResultBtn: "ಓದುವುದನ್ನು ನಿಲ್ಲಿಸಿ", // NEEDS HUMAN REVIEW
  voiceSummarySpeech: ({ cropName, votePct, within, total, reasons }) =>
    `ಅತ್ಯುತ್ತಮ ಶಿಫಾರಸು ಬೆಳೆ ${cropName}, ಶೇಕಡಾ ${votePct} ಮಾದರಿ ಮತ ಹಂಚಿಕೆ ಮತ್ತು ${total} ರಲ್ಲಿ ${within} ಅಂಶಗಳು ಸಾಮಾನ್ಯ ಮಿತಿಯಲ್ಲಿವೆ. ${reasons.join(". ")}`, // NEEDS HUMAN REVIEW
  loadingMsg: "ಉತ್ತಮ 3 ಬೆಳೆಗಳು ಮತ್ತು ಐತಿಹಾಸಿಕ ಬೆಲೆ ಶ್ರೇಣಿಗಳನ್ನು ಹುಡುಕಲಾಗುತ್ತಿದೆ...", // NEEDS HUMAN REVIEW
  emptyStatePrefix: "ಮೇಲಿನ ಉಷ್ಣಾಂಶ, ಆರ್ದ್ರತೆ ಮತ್ತು ಮಳೆ ವಿವರಗಳನ್ನು (ಹಾಗೂ ಲಭ್ಯವಿರುವ ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳನ್ನು) ನಮೂದಿಸಿ ಮತ್ತು ಕ್ಲಿಕ್ ಮಾಡಿ:", // NEEDS HUMAN REVIEW
  emptyStateAction: "ಬೆಳೆ ಶಿಫಾರಸು ಪಡೆಯಿರಿ", // NEEDS HUMAN REVIEW
  apiFixInputs: "ದಯವಿಟ್ಟು ಗುರುತಿಸಿದ ಮೌಲ್ಯಗಳನ್ನು ಸರಿಪಡಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.", // NEEDS HUMAN REVIEW
  apiServerError: (status) =>
    `ಸರ್ವರ್ ದೋಷ ${status} ಕಂಡುಬಂದಿದೆ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.`, // NEEDS HUMAN REVIEW
  apiDown:
    "ಬ್ಯಾಕೆಂಡ್ ಸೇವೆಯನ್ನು ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಸರ್ವರ್ ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿ.", // NEEDS HUMAN REVIEW
  errWeatherRequired: "ಈ ಹವಾಮಾನ ಮಾಹಿತಿ ಕಡ್ಡಾಯವಾಗಿದೆ.", // NEEDS HUMAN REVIEW
  errInvalidNumber: "ದಯವಿಟ್ಟು ಮಾನ್ಯವಾದ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ.", // NEEDS HUMAN REVIEW
  errOutOfRange: (min, max) => `ಮೌಲ್ಯವು ${min} ಮತ್ತು ${max} ನಡುವೆ ಇರಬೇಕು.`, // NEEDS HUMAN REVIEW
  errApiOutOfRange: (min, max) => `ಮಿತಿಯಿಂದ ಹೊರಗಿದೆ (${min} ರಿಂದ ${max}).`, // NEEDS HUMAN REVIEW
  errGenericInvalid: "ಅಮಾನ್ಯ ಮೌಲ್ಯ.", // NEEDS HUMAN REVIEW
  modeBanner: (modeLabel, pct) => `${modeLabel} · ನಿರೀಕ್ಷಿತ ನಿಖರತೆ ${pct}%`, // NEEDS HUMAN REVIEW
  modes: {
    A: "ವಿಧಾನ ಎ (ಸಂಪೂರ್ಣ ಮಣ್ಣಿನ ಮಾಹಿತಿ)", // NEEDS HUMAN REVIEW
    B: "ವಿಧಾನ ಬಿ (ಭಾಗಶಃ ಮಣ್ಣಿನ ಮಾಹಿತಿ)", // NEEDS HUMAN REVIEW
    C: "ವಿಧಾನ ಸಿ (ಮಣ್ಣಿನ ಮಾಹಿತಿ ಇಲ್ಲ)", // NEEDS HUMAN REVIEW
  },
  excludedProfitMsg: (cropsList) =>
    `ಲಾಭದ ಶ್ರೇಣಿಯಿಂದ ಹೊರಗಿಡಲಾದ ಬೆಳೆಗಳು (ಲಾಭದ ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ): ${cropsList}`, // NEEDS HUMAN REVIEW
  modelVoteShare: "ಮಾದರಿ ಮತ ಹಂಚಿಕೆ", // NEEDS HUMAN REVIEW
  conditionsInRange: (within, total) => `${total} ರಲ್ಲಿ ${within} ಅಂಶಗಳು ಸಾಮಾನ್ಯ ಮಿತಿಯಲ್ಲಿವೆ`, // NEEDS HUMAN REVIEW
  economicsTitle: "ಬೆಲೆ ಮತ್ತು ಲಾಭದ ಅಂದಾಜು", // NEEDS HUMAN REVIEW
  dataNotAvailable: "ಮಾಹಿತಿ ಲಭ್ಯವಿಲ್ಲ", // NEEDS HUMAN REVIEW
  econColMetric: "ಅಂಶ", // NEEDS HUMAN REVIEW
  econColLow: "ಕನಿಷ್ಠ", // NEEDS HUMAN REVIEW
  econColExpected: "ನಿರೀಕ್ಷಿತ", // NEEDS HUMAN REVIEW
  econColHigh: "ಗರಿಷ್ಠ", // NEEDS HUMAN REVIEW
  econRowPrice: "ಬೆಲೆ (ಪ್ರತಿ ಕ್ವಿಂಟಾಲ್)", // NEEDS HUMAN REVIEW
  econRowProfit: "ಲಾಭ (ಪ್ರತಿ ಎಕರೆ)", // NEEDS HUMAN REVIEW
  econNote: (months) =>
    `ಸಾಮಾನ್ಯ ಐತಿಹಾಸಿಕ ಶ್ರೇಣಿ, ಇದು ಖಾತ್ರಿಯಲ್ಲ. (${months} ತಿಂಗಳ ಬೆಲೆ ಇತಿಹಾಸ)`, // NEEDS HUMAN REVIEW
  howTitle: "ಇದನ್ನು ಹೇಗೆ ನಿರ್ಧರಿಸಲಾಯಿತು?", // NEEDS HUMAN REVIEW
  howBullets: [
    {
      heading: "ಮಣ್ಣಿನ ವಿಧಾನಗಳು (ಎ / ಬಿ / ಸಿ):", // NEEDS HUMAN REVIEW
      body: "ನೀವು ನೀಡುವ ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ಮೌಲ್ಯಗಳ ಸಂಯೋಜನೆಗೆ ಅನುಗುಣವಾಗಿ ಪ್ರತ್ಯೇಕ ರಾಂಡಮ್ ಫಾರೆಸ್ಟ್ ಮಾದರಿಯನ್ನು ಬಳಸಲಾಗುತ್ತದೆ. ವಿಧಾನ ಎ ಎಲ್ಲಾ 4 ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳನ್ನು, ವಿಧಾನ ಬಿ 1–3 ಮೌಲ್ಯಗಳನ್ನು, ಮತ್ತು ವಿಧಾನ ಸಿ ಕೇವಲ ಹವಾಮಾನವನ್ನು ಬಳಸುತ್ತದೆ.", // NEEDS HUMAN REVIEW
    },
    {
      heading: "ಕಡಿಮೆ ಮಣ್ಣಿನ ಮೌಲ್ಯಗಳಿಂದ ನಿಖರತೆ ಏಕೆ ಕಡಿಮೆಯಾಗುತ್ತದೆ:", // NEEDS HUMAN REVIEW
      body: "ಹಲವು ಬೆಳೆಗಳು ಒಂದೇ ರೀತಿಯ ಹವಾಮಾನದಲ್ಲಿ ಬೆಳೆಯಬಲ್ಲವು. ಸಾರಜನಕ, ರಂಜಕ, ಪೊಟ್ಯಾಸಿಯಮ್ ಮತ್ತು ಮಣ್ಣಿನ ಪಿಎಚ್ ಮೌಲ್ಯಗಳು ಬೆಳೆಗಳನ್ನು ಹೆಚ್ಚು ನಿಖರವಾಗಿ ಪ್ರತ್ಯೇಕಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ.", // NEEDS HUMAN REVIEW
    },
    {
      heading: "ಕಾರಣಗಳ ಅರ್ಥ:", // NEEDS HUMAN REVIEW
      body: "ಪ್ರತಿ ಸಾಲು ನಿಮ್ಮ ಮೌಲ್ಯವನ್ನು ಆ ಬೆಳೆಯ ಸಾಮಾನ್ಯ ಶ್ರೇಣಿಯೊಂದಿಗೆ (5ನೇಯಿಂದ 95ನೇ ಶೇಕಡಾವಾರು) ಹೋಲಿಸುತ್ತದೆ. ಹಸಿರು ಬಣ್ಣ ಮಿತಿಯೊಳಗಿದೆ ಎಂದೂ, ಕೆಂಪು ಬಣ್ಣ ಮಿತಿಗಿಂತ ಕಡಿಮೆ ಅಥವಾ ಹೆಚ್ಚು ಎಂದೂ ತೋರಿಸುತ್ತದೆ.", // NEEDS HUMAN REVIEW
    },
  ],
  fields: {
    temperature: {
      label: "ಉಷ್ಣಾಂಶ (ಸೆಲ್ಸಿಯಸ್)", // NEEDS HUMAN REVIEW
      placeholder: "ಉದಾ. 21", // NEEDS HUMAN REVIEW
      reasonName: "ಉಷ್ಣಾಂಶ", // NEEDS HUMAN REVIEW
      unit: "ಸೆ.", // NEEDS HUMAN REVIEW
    },
    humidity: {
      label: "ಆರ್ದ್ರತೆ (%)", // NEEDS HUMAN REVIEW
      placeholder: "ಉದಾ. 82", // NEEDS HUMAN REVIEW
      reasonName: "ಆರ್ದ್ರತೆ", // NEEDS HUMAN REVIEW
      unit: "%", // NEEDS HUMAN REVIEW
    },
    rainfall: {
      label: "ಮಳೆ (ಮಿ.ಮೀ.)", // NEEDS HUMAN REVIEW
      placeholder: "ಉದಾ. 203", // NEEDS HUMAN REVIEW
      reasonName: "ಮಳೆ", // NEEDS HUMAN REVIEW
      unit: "ಮಿ.ಮೀ.", // NEEDS HUMAN REVIEW
    },
    n: {
      label: "ಸಾರಜನಕ", // NEEDS HUMAN REVIEW
      placeholder: "ಐಚ್ಛಿಕ, ಉದಾ. 90", // NEEDS HUMAN REVIEW
      reasonName: "ಸಾರಜನಕ", // NEEDS HUMAN REVIEW
      unit: "", // NEEDS HUMAN REVIEW
    },
    p: {
      label: "ರಂಜಕ", // NEEDS HUMAN REVIEW
      placeholder: "ಐಚ್ಛಿಕ, ಉದಾ. 42", // NEEDS HUMAN REVIEW
      reasonName: "ರಂಜಕ", // NEEDS HUMAN REVIEW
      unit: "", // NEEDS HUMAN REVIEW
    },
    k: {
      label: "ಪೊಟ್ಯಾಸಿಯಮ್", // NEEDS HUMAN REVIEW
      placeholder: "ಐಚ್ಛಿಕ, ಉದಾ. 43", // NEEDS HUMAN REVIEW
      reasonName: "ಪೊಟ್ಯಾಸಿಯಮ್", // NEEDS HUMAN REVIEW
      unit: "", // NEEDS HUMAN REVIEW
    },
    ph: {
      label: "ಮಣ್ಣಿನ ಪಿಎಚ್", // NEEDS HUMAN REVIEW
      placeholder: "ಐಚ್ಛಿಕ, ಉದಾ. 6.5", // NEEDS HUMAN REVIEW
      reasonName: "ಮಣ್ಣಿನ ಪಿಎಚ್", // NEEDS HUMAN REVIEW
      unit: "", // NEEDS HUMAN REVIEW
    },
  },
  featureKeyToFieldKey: {
    N: "n",
    P: "p",
    K: "k",
    ph: "ph",
    temperature: "temperature",
    humidity: "humidity",
    rainfall: "rainfall",
  },
  formatReason: ({ name, value, low, high, unit, status, cropName }) => {
    const statusText =
      status === "within"
        ? "ಒಳಗೆ ಇದೆ" // NEEDS HUMAN REVIEW
        : status === "below"
          ? "ಗಿಂತ ಕಡಿಮೆ ಇದೆ" // NEEDS HUMAN REVIEW
          : "ಗಿಂತ ಹೆಚ್ಚು ಇದೆ"; // NEEDS HUMAN REVIEW
    return `${cropName} ಬೆಳೆಗೆ ${name} ${value}${unit} ಸಾಮಾನ್ಯ ಮಿತಿಯ (${low}-${high}${unit}) ${statusText}`; // NEEDS HUMAN REVIEW
  },
  crops: {
    rice: "ಭತ್ತ", // NEEDS HUMAN REVIEW
    maize: "ಮೆಕ್ಕೆಜೋಳ", // NEEDS HUMAN REVIEW
    chickpea: "ಕಡಲೆ", // NEEDS HUMAN REVIEW
    kidneybeans: "ರಾಜ್ಮಾ", // NEEDS HUMAN REVIEW
    pigeonpeas: "ತೊಗರಿ", // NEEDS HUMAN REVIEW
    mothbeans: "ಮಡಿಕೆ ಕಾಳು", // NEEDS HUMAN REVIEW
    mungbean: "ಹೆಸರು ಕಾಳು", // NEEDS HUMAN REVIEW
    blackgram: "ಉದ್ದು", // NEEDS HUMAN REVIEW
    lentil: "ಮಸೂರ್ ಬೇಳೆ", // NEEDS HUMAN REVIEW
    pomegranate: "ದಾಳಿಂಬೆ", // NEEDS HUMAN REVIEW
    banana: "ಬಾಳೆಹಣ್ಣು", // NEEDS HUMAN REVIEW
    mango: "ಮಾವು", // NEEDS HUMAN REVIEW
    grapes: "ದ್ರಾಕ್ಷಿ", // NEEDS HUMAN REVIEW
    watermelon: "ಕಲ್ಲಂಗಡಿ", // NEEDS HUMAN REVIEW
    muskmelon: "ಕರಬೂಜ", // NEEDS HUMAN REVIEW
    apple: "ಸೇಬು", // NEEDS HUMAN REVIEW
    orange: "ಕಿತ್ತಳೆ", // NEEDS HUMAN REVIEW
    papaya: "ಪಪ್ಪಾಯಿ", // NEEDS HUMAN REVIEW
    coconut: "ತೆಂಗು", // NEEDS HUMAN REVIEW
    cotton: "ಹತ್ತಿ", // NEEDS HUMAN REVIEW
    jute: "ಸೆಣಬು", // NEEDS HUMAN REVIEW
    coffee: "ಕಾಫಿ", // NEEDS HUMAN REVIEW
  },
};

export default kn;
