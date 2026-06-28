/**
 * Single source for backend API URLs.
 * Set VITE_API_BASE_URL in frontend/.env (local) or Vercel/host env vars (production).
 * Use the backend origin only — do not include /api/v1 (added automatically).
 *
 * Example: https://api.yourdomain.com
 * Local:   http://localhost:8000
 */
export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

export const API_V1_BASE_URL = `${API_BASE_URL}/api/v1`;
