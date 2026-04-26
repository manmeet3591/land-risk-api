"use client";

import { useState, useMemo } from "react";
import dynamic from "next/dynamic";

// Dynamically import MapPicker to avoid SSR issues with Leaflet
const MapPicker = dynamic(() => import("../components/MapPicker"), {
  ssr: false,
  loading: () => <div className="h-[400px] w-full bg-slate-200 animate-pulse rounded-2xl flex items-center justify-center">Loading Map...</div>,
});

const LAND_USES = [
  "Reforested Land",
  "Bioenergy Crop",
  "Agroforestry",
  "Cropland",
  "Grassland",
  "Urban/Built-up"
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [location, setLocation] = useState<{lat: number, lng: number} | null>(null);
  const [proposedUse, setProposedUse] = useState(LAND_USES[0]);

  const runScenario = async () => {
    if (!location) {
      alert("Please select a location on the map first.");
      return;
    }

    setLoading(true);
    try {
      // Use environment variable for production, fallback to localhost for dev
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const isLocal = window.location.hostname === "localhost";

      // If we are on the live site but no production API URL is set, 
      // we use the mock fallback. Otherwise, we hit the real API.
      if (isLocal || process.env.NEXT_PUBLIC_API_URL) {
        const response = await fetch(`${apiBase}/v1/score-scenario`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            lat: location.lat,
            lng: location.lng,
            proposed_use: proposedUse,
            area_hectares: 1000,
          }),
        });
        const data = await response.json();
        setResult(data);
      } else {
        // Fallback for live demo on GitHub Pages
        await new Promise((resolve) => setTimeout(resolve, 1500));
        // Simple mock logic for demo site
        const isForest = location.lat >= 0 && location.lat <= 15;
        setResult({
          current_use: isForest ? "Primary Forest" : "Cropland",
          tradeoff_vector: {
            carbon_score: isForest ? -0.4 : 0.6,
            biodiversity_score: isForest ? -0.8 : 0.3,
            food_security_score: -0.5
          },
          confidence: 0.85,
          red_flags: isForest ? ["Critical: Project involves conversion of primary forest"] : ["Loss of food production area"],
          recommendation: "Live Demo: Use local backend for real biophysical table lookups."
        });
      }
    } catch (error) {
      console.error("Error fetching scenario:", error);
      alert("Make sure the backend is running at http://localhost:8000");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-slate-50 text-slate-900">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm flex mb-12">
        <p className="flex w-auto justify-center border-b border-gray-300 bg-zinc-200/50 pb-4 pt-4 backdrop-blur-2xl rounded-xl border p-4">
          ⚖️ Land Risk API v1.0
        </p>
      </div>

      <div className="text-center max-w-4xl w-full">
        <h1 className="text-4xl font-black mb-4 text-slate-900">
          Land-Use Risk Engine
        </h1>
        <p className="text-lg text-slate-600 mb-10">
          Select a location and proposed change to see instant environmental trade-offs.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 text-left">
          {/* LEFT COLUMN: INPUTS */}
          <div className="space-y-8">
            <section>
              <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider mb-2">
                1. Select Location
              </label>
              <MapPicker onLocationSelect={(lat, lng) => setLocation({lat, lng})} />
              {location && (
                <p className="mt-2 text-xs text-blue-600 font-mono">
                  Coordinates: {location.lat.toFixed(4)}, {location.lng.toFixed(4)}
                </p>
              )}
            </section>

            <section>
              <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider mb-2">
                2. Proposed Land Use
              </label>
              <select 
                value={proposedUse}
                onChange={(e) => setProposedUse(e.target.value)}
                className="w-full p-4 bg-white border-2 border-slate-200 rounded-xl shadow-sm focus:border-blue-500 outline-none transition-all"
              >
                {LAND_USES.map(u => <option key={u} value={u}>{u}</option>)}
              </select>
            </section>

            <button
              onClick={runScenario}
              disabled={loading || !location}
              className="w-full bg-slate-900 hover:bg-black text-white font-black py-4 px-8 rounded-xl transition-all disabled:opacity-30 shadow-lg"
            >
              {loading ? "CALCULATING..." : "RUN TRADE-OFF ANALYSIS"}
            </button>
          </div>

          {/* RIGHT COLUMN: RESULTS */}
          <div>
            <label className="block text-sm font-bold text-slate-700 uppercase tracking-wider mb-2">
              3. Impact Results
            </label>
            {!result && !loading && (
              <div className="h-[500px] border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 p-8 text-center">
                <svg className="w-12 h-12 mb-4 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <p>Select a location and click run to generate scores.</p>
              </div>
            )}

            {loading && (
               <div className="h-[500px] bg-white border-2 border-slate-100 rounded-2xl flex flex-col items-center justify-center p-8 text-center animate-pulse">
                <p className="font-mono text-blue-600">Extracting spatial data...</p>
               </div>
            )}

            {result && !loading && (
              <div className="bg-white p-8 rounded-2xl shadow-xl border border-slate-200 animate-in fade-in zoom-in duration-300">
                <div className="flex justify-between items-center mb-6">
                   <h3 className="text-2xl font-black">Trade-offs</h3>
                   <span className="bg-slate-100 px-3 py-1 rounded-full text-xs font-bold text-slate-500">
                    Detected: {result.current_use}
                   </span>
                </div>
                
                <div className="grid grid-cols-1 gap-4 mb-8">
                  <ScoreBar label="Carbon Storage" score={result.tradeoff_vector.carbon_score} color="emerald" />
                  <ScoreBar label="Biodiversity" score={result.tradeoff_vector.biodiversity_score} color="blue" />
                  <ScoreBar label="Food Security" score={result.tradeoff_vector.food_security_score} color="orange" />
                </div>

                <div className="space-y-6 pt-6 border-t border-slate-100">
                  <div>
                    <p className="font-bold text-slate-800 uppercase text-[10px] tracking-[0.2em] mb-2">Scenario Recommendation</p>
                    <p className="text-slate-600 text-sm leading-relaxed">{result.recommendation}</p>
                  </div>
                  {result.red_flags.length > 0 && (
                    <div>
                      <p className="font-bold text-red-600 uppercase text-[10px] tracking-[0.2em] mb-2">Red Flags</p>
                      <ul className="space-y-2">
                        {result.red_flags.map((flag: string, i: number) => (
                          <li key={i} className="text-xs text-red-500 flex items-start gap-2">
                            <span>⚠️</span> {flag}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <footer className="mt-24 text-slate-400 text-[10px] uppercase tracking-widest">
        Science by InVEST &bull; Built for High-Integrity Decisions
      </footer>
    </main>
  );
}

function ScoreBar({ label, score, color }: { label: string, score: number, color: string }) {
  const percentage = Math.abs(score * 100);
  const isPositive = score >= 0;

  return (
    <div>
      <div className="flex justify-between text-xs font-bold mb-1 uppercase tracking-tight">
        <span>{label}</span>
        <span className={isPositive ? "text-emerald-600" : "text-red-600"}>
          {isPositive ? "+" : ""}{score}
        </span>
      </div>
      <div className="h-3 bg-slate-100 rounded-full overflow-hidden relative">
        <div 
          className={`h-full transition-all duration-1000 ${isPositive ? `bg-${color}-500` : "bg-red-400"}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
