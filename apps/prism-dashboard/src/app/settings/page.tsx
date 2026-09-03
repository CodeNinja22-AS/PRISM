"use client";

import { useEffect, useState } from "react";
import { Settings, Save, Server, Shield, BrainCircuit } from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    platt_a: -0.8,
    platt_b: 0.2,
    adversarial_strictness: 0.8,
    base_reliability: 0.85
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/settings/")
      .then(res => res.json())
      .then(data => setSettings(data))
      .catch(err => console.error("Failed to load settings:", err));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    try {
      await fetch("http://localhost:8000/api/v1/settings/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings)
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error(err);
    }
    setSaving(false);
  };

  const handleChange = (key: string, value: number) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="p-6 h-full flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4 border-b border-white/10 pb-4">
        <Settings className="text-cream" size={32} />
        <div>
          <h1 className="text-3xl font-bold text-cream tracking-tight">System Configuration</h1>
          <p className="text-sm text-silver mt-1">Tune ML parameters, confidence thresholds, and system behaviors</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
        
        {/* ML Tuning */}
        <div className="clay-card p-6 rounded-xl border border-white/5 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <BrainCircuit size={64} />
          </div>
          <h2 className="text-xl font-bold text-cream mb-6 flex items-center gap-2">
            Platt Scaling Calibration
          </h2>
          
          <div className="space-y-6 relative z-10">
            <div>
              <label className="flex justify-between text-sm text-silver mb-2">
                <span>Alpha (A) Parameter</span>
                <span className="font-mono text-primary">{settings.platt_a.toFixed(2)}</span>
              </label>
              <input 
                type="range" min="-2.0" max="0.0" step="0.1" 
                value={settings.platt_a} 
                onChange={(e) => handleChange("platt_a", parseFloat(e.target.value))}
                className="w-full accent-primary"
              />
              <p className="text-xs text-silver/60 mt-1">Controls curve steepness for probability calibration.</p>
            </div>
            
            <div>
              <label className="flex justify-between text-sm text-silver mb-2">
                <span>Beta (B) Parameter</span>
                <span className="font-mono text-primary">{settings.platt_b.toFixed(2)}</span>
              </label>
              <input 
                type="range" min="-1.0" max="1.0" step="0.1" 
                value={settings.platt_b} 
                onChange={(e) => handleChange("platt_b", parseFloat(e.target.value))}
                className="w-full accent-primary"
              />
              <p className="text-xs text-silver/60 mt-1">Controls inflection point offset.</p>
            </div>
          </div>
        </div>

        {/* Adversarial Tuning */}
        <div className="clay-card p-6 rounded-xl border border-white/5 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Shield size={64} />
          </div>
          <h2 className="text-xl font-bold text-cream mb-6 flex items-center gap-2">
            Adversarial Rules Engine
          </h2>
          
          <div className="space-y-6 relative z-10">
            <div>
              <label className="flex justify-between text-sm text-silver mb-2">
                <span>Strictness Penalty</span>
                <span className="font-mono text-red-400">{settings.adversarial_strictness.toFixed(2)}</span>
              </label>
              <input 
                type="range" min="0.0" max="1.0" step="0.05" 
                value={settings.adversarial_strictness} 
                onChange={(e) => handleChange("adversarial_strictness", parseFloat(e.target.value))}
                className="w-full accent-red-400"
              />
              <p className="text-xs text-silver/60 mt-1">Multiplier penalty when contradictions are found.</p>
            </div>
            
            <div>
              <label className="flex justify-between text-sm text-silver mb-2">
                <span>Base Evidence Reliability</span>
                <span className="font-mono text-green-400">{settings.base_reliability.toFixed(2)}</span>
              </label>
              <input 
                type="range" min="0.5" max="1.0" step="0.01" 
                value={settings.base_reliability} 
                onChange={(e) => handleChange("base_reliability", parseFloat(e.target.value))}
                className="w-full accent-green-400"
              />
              <p className="text-xs text-silver/60 mt-1">Default trust weight for new unknown evidence sources.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button 
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 bg-primary hover:bg-primary/80 text-background font-bold py-3 px-8 rounded-lg transition-all disabled:opacity-50"
        >
          <Save size={20} />
          {saving ? "Saving..." : saved ? "Saved!" : "Apply Configuration"}
        </button>
      </div>

    </div>
  );
}
