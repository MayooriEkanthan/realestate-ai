import { useEffect, useState } from "react";
import { api, lkr } from "../api.js";

export default function Price() {
  const [towns, setTowns] = useState([]);
  const [f, setF] = useState({ town: "", type: "House", bedrooms: 3, area_sqft: 1500, perches: 10 });
  const [result, setResult] = useState(null);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/api/towns").then((t) => { setTowns(t); setF((p) => ({ ...p, town: t[0] || "" })); })
      .catch((e) => setErr(e.message));
  }, []);

  const set = (k, v) => setF((p) => ({ ...p, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setResult(null); setLoading(true);
    try {
      setResult(await api.post("/api/predict", {
        ...f,
        bedrooms: Number(f.bedrooms),
        area_sqft: Number(f.area_sqft),
        perches: Number(f.perches),
      }));
    } catch (e2) { setErr(e2.message); }
    setLoading(false);
  };

  const input = "w-full border rounded-lg px-3 py-2 bg-white";
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Price Predictor</h2>
      <form onSubmit={submit} className="grid sm:grid-cols-2 gap-4 bg-white p-5 rounded-xl shadow-sm">
        <label className="text-sm">Town
          <select className={input} value={f.town} onChange={(e) => set("town", e.target.value)}>
            {towns.map((t) => <option key={t}>{t}</option>)}
          </select>
        </label>
        <label className="text-sm">Type
          <select className={input} value={f.type} onChange={(e) => set("type", e.target.value)}>
            {["House", "Apartment", "Land"].map((t) => <option key={t}>{t}</option>)}
          </select>
        </label>
        <label className="text-sm">Bedrooms
          <input type="number" min="0" max="15" className={input} value={f.bedrooms} onChange={(e) => set("bedrooms", e.target.value)} />
        </label>
        <label className="text-sm">Area (sq ft)
          <input type="number" min="0" className={input} value={f.area_sqft} onChange={(e) => set("area_sqft", e.target.value)} />
        </label>
        <label className="text-sm">Land (perches)
          <input type="number" min="0" className={input} value={f.perches} onChange={(e) => set("perches", e.target.value)} />
        </label>
        <div className="flex items-end">
          <button disabled={loading} className="bg-emerald-600 text-white px-5 py-2 rounded-lg disabled:opacity-50">
            {loading ? "Estimating..." : "Estimate price"}
          </button>
        </div>
      </form>
      {err && <p className="mt-4 text-red-600">{err}</p>}
      {result && (
        <div className="mt-6 bg-emerald-50 border border-emerald-200 p-5 rounded-xl">
          <p className="text-sm text-slate-600">Estimated price</p>
          <p className="text-3xl font-bold text-emerald-700">{lkr(result.estimated_price_lkr)}</p>
          <p className="text-xs text-slate-500 mt-2">{result.note}</p>
        </div>
      )}
    </div>
  );
}
