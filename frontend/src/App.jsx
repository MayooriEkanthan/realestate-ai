import { useState } from "react";
import Listings from "./pages/Listings.jsx";
import ListingDetail from "./pages/ListingDetail.jsx";
import Price from "./pages/Price.jsx";
import Describe from "./pages/Describe.jsx";

const NAV = [
  { id: "listings", label: "Browse Listings" },
  { id: "price", label: "Price Predictor" },
  { id: "describe", label: "Description Writer" },
];

export default function App() {
  const [page, setPage] = useState("listings");
  const [listingId, setListingId] = useState(null);

  const openListing = (id) => { setListingId(id); setPage("detail"); };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-slate-50 text-slate-800">
      <aside className="md:w-60 bg-slate-900 text-slate-100 p-4 md:min-h-screen">
        <h1 className="text-xl font-bold mb-1">Real Estate AI</h1>
        <p className="text-xs text-slate-400 mb-6">Sri Lanka prototype</p>
        <nav className="flex md:flex-col gap-2 flex-wrap">
          {NAV.map((n) => (
            <button
              key={n.id}
              onClick={() => setPage(n.id)}
              className={`text-left px-3 py-2 rounded-lg text-sm ${
                page === n.id || (page === "detail" && n.id === "listings")
                  ? "bg-emerald-600 text-white"
                  : "hover:bg-slate-800"
              }`}
            >
              {n.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="flex-1 p-4 md:p-8 max-w-5xl">
        {page === "listings" && <Listings onOpen={openListing} />}
        {page === "detail" && <ListingDetail id={listingId} onBack={() => setPage("listings")} />}
        {page === "price" && <Price />}
        {page === "describe" && <Describe />}
        <footer className="mt-10 text-xs text-slate-500">
          Prototype using simulated data. Not financial or legal advice. No real payments.
        </footer>
      </main>
    </div>
  );
}
