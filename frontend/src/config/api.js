export function apiUrl(path) {
  const raw = import.meta.env.VITE_API_ORIGIN;
  const origin =
    typeof raw === "string" ? raw.trim().replace(/\/$/, "") : "";
  const p = path.startsWith("/") ? path : `/${path}`;
  return origin ? `${origin}${p}` : p;
}
