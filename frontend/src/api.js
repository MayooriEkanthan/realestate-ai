const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }
  let data = null;
  try { data = await res.json(); } catch { /* no body */ }
  if (!res.ok) {
    const d = data?.detail;
    const msg = typeof d === "string" ? d
      : Array.isArray(d) ? d.map((x) => x.msg).join(", ")
      : "Request failed";
    throw new Error(msg);
  }
  return data;
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
};

export const lkr = (n) =>
  "LKR " + Number(n).toLocaleString("en-LK", { maximumFractionDigits: 0 });
