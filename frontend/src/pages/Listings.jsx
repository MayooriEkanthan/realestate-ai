import { useEffect, useState } from "react";
import { api, lkr } from "../api.js";

export default function Listings({ onOpen }) {
  const [towns, setTowns] = useState([]);
  const [filters, setFilters] = useState({ town: "", type: "", min_bedrooms: 0, max_price: "" });
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async (f = filters) => {
    setErr(""); setLoading(true);
    const p = new URLSearchParams();
    if (f.town) p.set("town", f.town);
    if (f.type) p.set("type", f.type);
    if (Number(f.min_bedrooms) > 0) p.set("min_bedrooms", f.min_bedrooms);
    if (f.max_price) p.set("max_price", f.max_price);
    try { setItems(await api.get("/api/listings?" + p.toString())); }
    catch (e) { setErr(e.message); }
    setLoading(false);
  };

  useEffect(() => {
    api.get("/api/towns").then(setTowns).catch(() => {});
    load();
    // eslint-disable-next-line
  }, []);

  const set = (k, v) => setFilters((p) => ({ ...p, [k]: v }));
  const input = "border rounded-lg px-3 py-2 bg-white text-sm";

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Browse Listings</h2>
      <div className="flex flex-wrap gap-3 mb-6">
        <select className={input} value={filters.town} onChange={(e) => set("town", e.target.value)}>
          <option value="">All towns</option>
          {towns.map((t) => <option key={t}>{t}</option>)}
        </select>
        <select className={input} value={filters.type} onChange={(e) => set("type", e.target.value)}>
          <option value="">All types</option>
          {["House", "Apartment", "Land"].map((t) => <option key={t}>{t}</option>)}
        </select>
        <input type="number" min="0" placeholder="Min bedrooms" className={input + " w-36"}
          onChange={(e) => set("min_bedrooms", e.target.value || 0)} />
        <input type="number" min="0" placeholder="Max price (LKR)" className={input + " w-44"}
          onChange={(e) => set("max_price", e.target.value)} />
        <button onClick={() => load()} className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm">
          Search
        </button>
      </div>

      {err && <p className="text-red-600 mb-4">{err}</p>}
      {loading && <p className="text-slate-500">Loading...</p>}
      {!loading && !err && items.length === 0 && <p className="text-slate-500">No listings match.</p>}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {items.map((l) => (
          <button key={l.id} onClick={() => onOpen(l.id)}
            className="text-left bg-white p-4 rounded-xl shadow-sm hover:shadow-md transition">
            <p className="text-xs text-emerald-700 font-semibold">{l.type} · {l.town}</p>
            <p className="mt-1 font-semibold">{l.description}</p>
            <p className="mt-3 text-lg font-bold">{lkr(l.price_lkr)}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
