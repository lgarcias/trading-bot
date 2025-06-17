// Utilidad para obtener la URL base de la API según entorno
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export function apiUrl(path) {
  // Si path ya es absoluta, no la modifica
  if (path.startsWith('http')) return path;
  return `${API_BASE}${path}`;
}

// Utility to handle fetch with error handling (migrated from App.jsx)
export async function fetchWithErrorHandling(url, options = {}) {
  const res = await fetch(url, options);
  let data;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }
  if (!res.ok) {
    // Prefer detail if present (FastAPI error), else status text
    const errorMsg = (data && data.detail && (typeof data.detail === 'string' ? data.detail : data.detail.msg)) || res.statusText || 'Unknown error';
    throw new Error(errorMsg);
  }
  return data;
}
