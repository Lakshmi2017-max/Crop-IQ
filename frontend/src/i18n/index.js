import en from "./en.js";
import kn from "./kn.js";

export const TRANSLATIONS = { en, kn };

export function formatNum(val) {
  const rounded = Math.round(Number(val) * 100) / 100;
  return Number.isInteger(rounded) ? String(rounded) : String(rounded);
}

export function translateCropName(t, crop) {
  return t.crops[crop] || crop;
}

export function buildTranslatedReason(t, detail, crop) {
  const fieldKey = t.featureKeyToFieldKey[detail.feature] || detail.feature;
  const fieldMeta = t.fields[fieldKey] || { reasonName: detail.feature, unit: "" };
  return t.formatReason({
    name: fieldMeta.reasonName,
    value: formatNum(detail.value),
    low: formatNum(detail.low),
    high: formatNum(detail.high),
    unit: fieldMeta.unit,
    status: detail.status,
    cropName: translateCropName(t, crop),
  });
}

export function getModeLabel(t, modeStr, soilValuesUsed) {
  const count = Array.isArray(soilValuesUsed) ? soilValuesUsed.length : 0;
  if (count === 4 || (modeStr && modeStr.startsWith("A"))) {
    return t.modes.A;
  }
  if (count >= 1 || (modeStr && modeStr.startsWith("B"))) {
    return t.modes.B;
  }
  return t.modes.C;
}
