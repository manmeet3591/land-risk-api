"use client";

import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runMockDemo = async () => {
    setLoading(true);
    try {
      // On the live GitHub Pages site, the backend won't be running.
      // We check if we are on localhost; if not, we use the mock data directly.
      if (window.location.hostname === "localhost") {
        const response = await fetch("http://localhost:8000/v1/score-scenario", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            location: "Amazon Rainforest Basin",
            current_use: "cropland",
            proposed_use: "reforestation",
            area_hectares: 1000,
          }),
        });
        const data = await response.json();
        setResult(data);
      } else {
        // Fallback for live demo on GitHub Pages
        await new Promise((resolve) => setTimeout(resolve, 1500)); // Simulate delay
        setResult({
          tradeoff_vector: {
            carbon_score: 0.85,
            biodiversity_score: 0.42,
            food_security_score: -0.61
          },
          confidence: 0.78,
          red_flags: ["High food production displacement detected (Live Demo Mode)"],
          recommendation: "Consider agroforestry to mitigate food security loss."
        });
      }
    } catch (error) {
      console.error("Error fetching mock data:", error);
      // Fallback in case of any error
      setResult({
        tradeoff_vector: {
          carbon_score: 0.85,
          biodiversity_score: 0.42,
          food_security_score: -0.61
        },
        confidence: 0.78,
        red_flags: ["Simulated data (Backend connection failed)"],
        recommendation: "Consider agroforestry to mitigate food security loss."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-50 text-slate-900">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm flex mb-12">
        <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
          ⚖️ Land Risk API
        </p>
      </div>

      <div className="text-center max-w-3xl">
        <h1 className="text-5xl font-bold mb-6">
          Instant land-use risk intelligence for climate and investment decisions.
        </h1>
        <p className="text-xl text-slate-600 mb-10">
          We help investors and climate companies understand the hidden trade-offs 
          of land use across Carbon, Biodiversity, and Food Security.
        </p>

        <div className="flex gap-4 justify-center mb-12">
          <button
            onClick={runMockDemo}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg transition-all disabled:opacity-50"
          >
            {loading ? "Calculating..." : "Run Demo Scenario"}
          </button>
        </div>

        {result && (
          <div className="bg-white p-8 rounded-2xl shadow-xl border border-slate-200 text-left animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-2xl font-bold mb-4">Tradeoff Analysis Results</h3>
            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100">
                <p className="text-emerald-800 text-sm font-bold uppercase tracking-wider mb-1">Carbon</p>
                <p className="text-3xl font-black text-emerald-900">+{result.tradeoff_vector.carbon_score}</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                <p className="text-blue-800 text-sm font-bold uppercase tracking-wider mb-1">Biodiversity</p>
                <p className="text-3xl font-black text-blue-900">+{result.tradeoff_vector.biodiversity_score}</p>
              </div>
              <div className="p-4 bg-orange-50 rounded-xl border border-orange-100">
                <p className="text-orange-800 text-sm font-bold uppercase tracking-wider mb-1">Food Security</p>
                <p className="text-3xl font-black text-orange-900">{result.tradeoff_vector.food_security_score}</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <p className="font-bold text-slate-800 uppercase text-xs tracking-widest mb-1">Recommendation</p>
                <p className="text-slate-700">{result.recommendation}</p>
              </div>
              <div>
                <p className="font-bold text-slate-800 uppercase text-xs tracking-widest mb-1">Red Flags</p>
                <ul className="list-disc list-inside text-slate-700">
                  {result.red_flags.map((flag: string, i: number) => (
                    <li key={i}>{flag}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      <footer className="mt-24 text-slate-400 text-sm">
        Powered by InVEST Science. Built for Climate Decision-Makers.
      </footer>
    </main>
  );
}
