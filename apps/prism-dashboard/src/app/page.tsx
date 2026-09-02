import Link from "next/link";
import { Activity, Target, Layers } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold font-['Space_Grotesk'] mb-2">Command Center</h1>
        <p className="text-platinum/60">Overview of active intelligence clusters.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="clay-card p-6 flex flex-col items-center text-center">
          <Activity size={32} className="mb-2" />
          <h2 className="text-4xl font-bold font-['Space_Grotesk']">14</h2>
          <p className="text-sm font-semibold opacity-70">Active Traces</p>
        </div>
        <div className="clay-card p-6 flex flex-col items-center text-center">
          <Target size={32} className="mb-2" />
          <h2 className="text-4xl font-bold font-['Space_Grotesk']">3</h2>
          <p className="text-sm font-semibold opacity-70">High-Confidence Attributes</p>
        </div>
        <div className="clay-card p-6 flex flex-col items-center text-center">
          <Layers size={32} className="mb-2" />
          <h2 className="text-4xl font-bold font-['Space_Grotesk']">8</h2>
          <p className="text-sm font-semibold opacity-70">Monitored Personas</p>
        </div>
      </div>

      <h2 className="text-2xl font-bold font-['Space_Grotesk'] mt-10 mb-4">Active Investigations</h2>
      <div className="space-y-4">
        <Link href="/investigation/TA-017" className="block">
          <div className="glass-panel p-6 flex items-center justify-between hover:bg-white/10 transition">
            <div>
              <h3 className="text-xl font-bold text-cream">TA-017 (Alpha)</h3>
              <p className="text-sm text-platinum/70">Last updated: 2 hours ago</p>
            </div>
            <div className="flex gap-4 text-sm">
              <span className="bg-green-500/20 text-green-300 px-3 py-1 rounded-full border border-green-500/30">
                Confidence: 93.4%
              </span>
              <span className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full border border-blue-500/30">
                Robustness: 82.1%
              </span>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
}
