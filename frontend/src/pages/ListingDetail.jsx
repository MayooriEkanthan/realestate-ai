import { useEffect, useState } from "react";
import { api, lkr } from "../api.js";

export default function ListingDetail({ id, onBack }) {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ buyer_name: "", buyer_phone: "", buyer_email: "", message: "", consent: false });
  const [sent, setSent] = useState(null);
  const [formErr, setFormErr] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    setData(null); setErr(""); setSent(null); setShowForm(false);
    api.get(`/api/listings/${id}`).then(setData).catch((e) => setErr(e.message));
  }, [id]);

  const set = (k, v) => setForm((p) => ({ ...p, [k]: v }));

  const send = async (e) => {
    e.preventDefault();
    setFormErr(""); setSending(true);
    try {
      setSent(await api.post("/api/inquiries", { listing_id: id, ...form }));
    } catch (e2) { setFormErr(e2.message); }
    setSending(false);
  };

  if (err) return <div><button onClick={onBack} className="underline mb-4">Back</button><p className="text-red-600">{err}</p></div>;
  if (!data) return <p className="text-slate-500">Loading...</p>;

  const { listing: l, agent: a, fee_terms: t, price_check: pc, safety_notice } = data;
  const input = "w-full border rounded-lg px-3 py-2 bg-white text-sm";
  const waText = encodeURIComponent(`Hi, I'm interested in listing #${l.id}: ${l.description}`);

  return (
    <div>
      <button onClick={onBack} className="text-sm underline mb-4">← Back to listings</button>

      <div className="bg-white p-6 rounded-xl shadow-sm">
        <p className="text-xs text-emerald-700 font-semibold">{l.type} · {l.town}</p>
        <h2 className="text-2xl font-bold mt-1">{l.description}</h2>
        <p className="text-3xl font-bold mt-3">{lkr(l.price_lkr)}</p>
        <p className="text-sm text-slate-600 mt-2">
          {l.bedrooms > 0 && `${l.bedrooms} bedrooms · `}
          {l.area_sqft > 0 && `${l.area_sqft} sq ft · `}
          {l.perches > 0 && `${l.perches} perches`}
        </p>

        {pc && (
          <div className={`mt-4 p-3 rounded-lg text-sm ${
            pc.flag === "SUSPICIOUSLY_LOW" ? "bg-red-50 border border-red-200 text-red-800"
            : pc.flag === "HIGH" ? "bg-amber-50 border border-amber-200 text-amber-800"
            : "bg-emerald-50 border border-emerald-200 text-emerald-800"}`}>
            AI estimate: {lkr(pc.estimated_price_lkr)}.{" "}
            {pc.flag === "SUSPICIOUSLY_LOW" && "This price is much lower than the estimate. Verify carefully before paying anything."}
            {pc.flag === "HIGH" && "This price is higher than the estimate."}
            {pc.flag === "OK" && "The listed price is in the expected range."}
            <span className="block text-xs opacity-75 mt-1">Prototype model on simulated data.</span>
          </div>
        )}
      </div>

      {t && (
        <div className="mt-4 bg-white p-5 rounded-xl shadow-sm text-sm">
          <h3 className="font-semibold mb-2">Agent fee terms (locked, version {t.version})</h3>
          <p>Commission: <b>{t.commission_pct}%</b>, paid by the <b>{t.payer}</b></p>
          <p>Due: {t.due_when}</p>
          <p>Covers: {t.covers}</p>
          <p>Other fees: {t.other_fees}</p>
          <p className="text-xs text-slate-500 mt-2">The agent cannot change these terms for your inquiry after you send it.</p>
        </div>
      )}

      {a && (
        <div className="mt-4 bg-white p-5 rounded-xl shadow-sm">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold">{a.name}</h3>
            {a.verified
              ? <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Verified (demo)</span>
              : <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">Not verified</span>}
          </div>
          <p className="text-sm text-slate-600">{a.agency} · {a.town} · {a.years_experience} yrs</p>
          <p className="text-sm mt-2">{a.bio}</p>
          <div className="flex flex-wrap gap-3 mt-4">
            <a href={`tel:+${a.phone}`} className="px-4 py-2 rounded-lg border text-sm">Call</a>
            <a href={`https://wa.me/${a.phone}?text=${waText}`} target="_blank" rel="noreferrer"
              className="px-4 py-2 rounded-lg bg-green-600 text-white text-sm">WhatsApp</a>
            <button onClick={() => setShowForm((s) => !s)}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm">
              Send inquiry
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2">Agent details are fictional demo data.</p>
        </div>
      )}

      {showForm && !sent && (
        <form onSubmit={send} className="mt-4 bg-white p-5 rounded-xl shadow-sm space-y-3">
          <h3 className="font-semibold">Contact the agent</h3>
          <input required minLength={2} className={input} placeholder="Your name" value={form.buyer_name} onChange={(e) => set("buyer_name", e.target.value)} />
          <input required minLength={7} className={input} placeholder="Phone" value={form.buyer_phone} onChange={(e) => set("buyer_phone", e.target.value)} />
          <input type="email" className={input} placeholder="Email (optional)" value={form.buyer_email} onChange={(e) => set("buyer_email", e.target.value)} />
          <textarea required minLength={3} rows="3" className={input} placeholder="Your message" value={form.message} onChange={(e) => set("message", e.target.value)} />
          <label className="flex gap-2 text-sm items-start">
            <input type="checkbox" checked={form.consent} onChange={(e) => set("consent", e.target.checked)} className="mt-1" />
            I agree to be contacted by this agent about this listing.
          </label>
          {formErr && <p className="text-red-600 text-sm">{formErr}</p>}
          <button disabled={sending || !form.consent} className="bg-emerald-600 text-white px-5 py-2 rounded-lg disabled:opacity-50">
            {sending ? "Sending..." : "Send"}
          </button>
        </form>
      )}

      {sent && (
        <div className="mt-4 bg-emerald-50 border border-emerald-200 p-5 rounded-xl text-sm">
          <p className="font-semibold">Inquiry sent</p>
          <p>Reference: <b>{sent.reference}</b>. Keep it, because it proves the terms you were shown.</p>
          <p>Price at inquiry: {lkr(sent.snapshot.listed_price_lkr)} · Commission: {sent.snapshot.commission_pct}%</p>
        </div>
      )}

      <p className="mt-4 text-xs text-slate-600 bg-amber-50 border border-amber-200 p-3 rounded-lg">{safety_notice}</p>
    </div>
  );
}
