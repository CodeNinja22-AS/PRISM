"use client";

import { useEffect, useState } from "react";
import ActorGraph from "@/components/ActorGraph";
import { useParams } from "next/navigation";
import { AlertTriangle, ShieldCheck, Zap } from "lucide-react";

export default function InvestigationPage() {
  const params = useParams();
  const id = params.id as string;

  const [invData, setInvData] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [invRes, graphRes] = await Promise.all([
          fetch(`http://127.0.0.1:8000/api/v1/analysis/investigation/${id}`),
          fetch(`http://127.0.0.1:8000/api/v1/graph/topology/${id}`)
        ]);
        
        if (invRes.ok && graphRes.ok) {
          setInvData(await invRes.json());
          setGraphData(await graphRes.json());
        }
      } catch (err) {
        console.error("Failed to fetch data", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id]);

  if (loading) {
    return <div className="p-10 text-center text-platinum animate-pulse">Establishing secure link to PRISM Engine...</div>;
  }

  if (!invData || !graphData) {
    return (
      <div className="p-10">
        <h1 className="text-2xl text-red-400">Error connecting to PRISM Backend</h1>
        <p className="opacity-70">Ensure the FastAPI server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] gap-4">
      {/* Header */}
      <header className="flex items-center justify-between glass-panel p-6 shrink-0">
        <div>
          <h1 className="text-3xl font-bold font-['Space_Grotesk'] text-cream">Investigation: {invData.title}</h1>
          <p className="text-platinum/60 tracking-wider">ID: {invData.id}</p>
        </div>
        
        <div className="flex gap-6">
          <div className="clay-card px-6 py-3 flex items-center gap-4">
            <ShieldCheck size={28} className="text-green-600" />
            <div>
              <div className="text-sm opacity-70 font-semibold uppercase">Confidence</div>
              <div className="text-2xl font-bold font-['Space_Grotesk']">{(invData.metrics.confidence * 100).toFixed(1)}%</div>
            </div>
          </div>
          
          <div className="clay-card px-6 py-3 flex items-center gap-4">
            <Zap size={28} className="text-blue-600" />
            <div>
              <div className="text-sm opacity-70 font-semibold uppercase">Robustness</div>
              <div className="text-2xl font-bold font-['Space_Grotesk']">{(invData.metrics.robustness * 100).toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Split */}
      <div className="flex flex-1 gap-4 overflow-hidden">
        {/* Left Panel: Graph */}
        <div className="w-3/5 glass-panel p-1 relative overflow-hidden flex flex-col">
          <div className="absolute top-4 left-4 z-10 bg-midnight/80 px-4 py-2 rounded-lg border border-white/10 text-sm font-semibold">
            Topology Map
          </div>
          <div className="flex-1">
            <ActorGraph initialNodes={graphData.nodes} initialEdges={graphData.edges} />
          </div>
        </div>

        {/* Right Panel: Data */}
        <div className="w-2/5 flex flex-col gap-4 overflow-y-auto pr-2">
          
          {/* Evidence Panel */}
          <div className="glass-panel p-6">
            <h2 className="text-xl font-bold font-['Space_Grotesk'] mb-4 text-cream border-b border-white/10 pb-2">Evidence Matrix</h2>
            <div className="space-y-6">
              {invData.evidence_breakdown.map((ev: any, idx: number) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-semibold">{ev.name} <span className="opacity-50 text-xs ml-2">({ev.group})</span></span>
                    <span className="font-mono text-cream">{(ev.score).toFixed(2)}</span>
                  </div>
                  <div className="h-2 progress-bar-bg">
                    <div 
                      className="progress-bar-fill" 
                      style={{ width: `${ev.score * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Adversarial Panel */}
          <div className="glass-panel p-6 border-t-2 border-t-red-500/50">
            <div className="flex items-center gap-3 mb-4 border-b border-white/10 pb-2">
              <AlertTriangle className="text-red-400" />
              <h2 className="text-xl font-bold font-['Space_Grotesk'] text-red-100">Counter-Hypotheses</h2>
            </div>
            
            <div className="space-y-4">
              {invData.adversarial_report.questions.map((q: string, idx: number) => (
                <div key={idx} className="bg-red-950/30 p-3 rounded-lg border border-red-500/20 text-sm text-red-200">
                  {q}
                </div>
              ))}
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-bold uppercase opacity-70 mb-2">Leave-One-Out Vulnerability</h3>
              <div className="text-sm bg-black/20 p-3 rounded-lg border border-white/5 font-mono text-platinum/80 flex flex-col gap-2">
                {Object.entries(invData.adversarial_report.leave_one_out).map(([group, val]: any) => (
                  <div key={group} className="flex justify-between">
                    <span>Without {group}:</span>
                    <span className={val < 0.8 ? "text-red-400" : "text-green-400"}>{(val*100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
