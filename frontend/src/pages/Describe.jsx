import { useState } from "react";
import { api } from "../api.js";

export default function Describe() {
  const [details, setDetails] = useState(
    "3 bedroom house in Kandy, 1800 sqft, 12 perches, near a school, with a garden");
  const [tone, setTone] = useState("friendly");
  const [text, setText] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const generate = async () => {
    setErr(""); setText(""); setCopied(false); setLoading(true);
    try {
      const r = await api.post("/api/describe", { details, tone });
      setText(r.description);
    } catch (e) { setErr(e.message); }
    setLoading(false);
  };

  const copy = async () => {
    try { await navigator.clipboard.writeText(text); setCopied(true); } catch { /* ignore */ }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Description Writer</h2>
      <div className="bg-white p-5 rounded-xl shadow-sm space-y-3">
        <label className="text-sm block">Property facts (only true details)
          <textarea rows="4" className="w-full border rounded-lg px-3 py-2 mt-1"
            value={details} onChange={(e) => setDetails(e.target.value)} />
        </label>
        <div className="flex gap-3 items-center">
          <select className="border rounded-lg px-3 py-2 bg-white" value={tone} onChange={(e) => setTone(e.target.value)}>
            <option value="friendly">Friendly</option>
            <option value="professional">Professional</option>
            <option value="luxury">Luxury</option>
          </select>
          <button onClick={generate} disabled={loading || details.length < 10}
            className="bg-emerald-600 text-white px-5 py-2 rounded-lg disabled:opacity-50">
            {loading ? "Writing..." : "Write description"}
          </button>
        </div>
      </div>
      {err && <p className="mt-4 text-red-600">{err}</p>}
      {text && (
        <div className="mt-6 bg-white p-5 rounded-xl shadow-sm">
          <p className="leading-relaxed">{text}</p>
          <button onClick={copy} className="mt-3 text-sm text-emerald-700 underline">
            {copied ? "Copied" : "Copy"}
          </button>
          <p className="text-xs text-slate-500 mt-2">AI-written draft. Check every detail before publishing.</p>
        </div>
      )}
    </div>
  );
}
