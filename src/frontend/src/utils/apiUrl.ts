// Centralized, auto-sanitizing API_URL
const rawEnvUrl = import.meta.env.VITE_API_URL;

function getSanitizedApiUrl(): string {
  if (rawEnvUrl && typeof rawEnvUrl === "string") {
    const trimmed = rawEnvUrl.trim().split(/\s+/)[0];
    if (trimmed.startsWith("http://") || trimmed.startsWith("https://") || trimmed.startsWith("/")) {
      return trimmed.replace(/\/+$/, ""); // remove trailing slash
    }
  }

  if (import.meta.env.DEV) {
    return "http://localhost:8000/api";
  }

  return "https://focus-flow-app-ashy.vercel.app/api";
}

export const API_URL = getSanitizedApiUrl();
