"use client";

import { useState } from 'react';
import CryptoAnalysis from '@/components/CryptoAnalysis';

export default function Home() {
  const [symbol, setSymbol] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol) return;
    setIsAnalyzing(true);
    // Analysis will be handled by the component
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-50">
      <h1 className="text-4xl font-bold mb-8 text-center">Cryptosys</h1>
      <p className="text-center text-lg mb-8 max-w-2xl">
        Analyze cryptocurrencies with combined technical and sentiment analysis.
      </p>
      
      <form onSubmit={handleAnalyze} className="w-full max-w-md mb-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            placeholder="Enter crypto symbol (e.g., BTC)"
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={!symbol || isAnalyzing}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Analyze
          </button>
        </div>
      </form>

      {symbol && <CryptoAnalysis symbol={symbol} setIsAnalyzing={setIsAnalyzing} />}
    </main>
  );
}