// Utilidad para obtener la URL base de la API según entorno
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export function apiUrl(path) {
  // Si path ya es absoluta, no la modifica
  if (path.startsWith('http')) return path;
  return `${API_BASE}${path}`;
}
