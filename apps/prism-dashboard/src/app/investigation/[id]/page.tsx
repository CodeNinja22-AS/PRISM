"use client";

import { useEffect, useState } from "react";
import ActorGraph from "@/components/ActorGraph";
import { useParams } from "next/navigation";
import { 
  AlertTriangle, ShieldCheck, Zap, Activity, BrainCircuit, 
  Crosshair, Network, Database, Wifi, User, Lock, FileText, 
  AlertOctagon, Clock 
} from "lucide-react";

export default function InvestigationPage() {
  const params = useParams();
  const id = params.id as string;

  const [loading, setLoading] = useState(true);
  const [invData, setInvData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch graph topology
        const graphRes = await fetch(`http://localhost:8000/api/v1/graph/topology?cluster_id=${id}`);
        const graphData = await graphRes.json();
        
        // Fetch cluster ML stats
        const clustersRes = await fetch(`http://localhost:8000/api/v1/clusters/all`);
        const clustersData = await clustersRes.json();
        const cluster = clustersData.clusters.find((c: any) => c.id === id) || { confidence: 0.94, robustness: 0.88 };

        // Construct live data object merging mock AI analysis with real graph data
        const liveData = {
          id: id,
          title: `Operation Alpha (${id})`,
          metrics: {
            confidence: cluster.confidence,
            robustness: cluster.robustness,
            driftScore: 0.12,
            metadataHits: 3
          },
          traffic: {
            prediction: "Video Streaming (Camouflage)",
            probabilities: {"Video": 0.82, "Web": 0.12, "Chat": 0.06},
            driftAlert: false
          },
          behavior: {
            latencyScore: 0.95,
            activeHoursScore: 0.30,
            pattern: "A → B → C → A"
          },
          metadata: [
            { type: "EXIF GPS", value: "37.7749,-122.4194", personas: ["Target_Alpha", "Suspect_Bravo"] },
            { type: "Device", value: "iPhone 13 Pro", personas: ["Target_Alpha"] }
          ],
          evidence_breakdown: [
            { name: "Traffic Timing", group: "Network", score: 0.92, reliability: 0.95 },
            { name: "Wallet Co-spending", group: "Blockchain", score: 0.87, reliability: 0.99 },
            { name: "Linguistic Profile", group: "Stylometry", score: 0.74, reliability: 0.60 }
          ],
          adversarial_report: {
            stress_test: [
              { noise: 0.10, confidence: 0.91 },
              { noise: 0.20, confidence: 0.82 },
              { noise: 0.30, confidence: 0.49 }
            ],
            contradictions: [
              { message: "WEAK CONTRADICTION: Conflicting timezone patterns.", penalty: 0.15 }
            ]
          },
          graph: graphData
        };
        
        setInvData(liveData);
      } catch (err) {
        console.error("Failed to load investigation data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (loading || !invData) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-2rem)]">
        <div className="text-center text-platinum animate-pulse flex flex-col items-center gap-4">
          <BrainCircuit size={48} className="text-cream" />
          <p className="text-xl font-['Space_Grotesk'] tracking-widest uppercase">Connecting to PRISM Intelligence Core...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen gap-4 pb-10">
      {/* 1. TOP ROW: KPI CARDS */}
      <header className="grid grid-cols-1 md:grid-cols-4 gap-4 shrink-0">
        
        <div className="glass-panel p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <ShieldCheck size={64} />
          </div>
          <div className="text-sm opacity-70 font-semibold uppercase mb-2 text-green-300">Calibrated Confidence</div>
          <div className="text-4xl font-bold font-['Space_Grotesk'] text-cream">{(invData.metrics.confidence * 100).toFixed(1)}%</div>
          <div className="text-xs opacity-60 mt-2">Bayesian fused (Platt scaled)</div>
        </div>

        <div className="glass-panel p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Zap size={64} />
          </div>
          <div className="text-sm opacity-70 font-semibold uppercase mb-2 text-blue-300">Robustness Score</div>
          <div className="text-4xl font-bold font-['Space_Grotesk'] text-cream">{(invData.metrics.robustness * 100).toFixed(1)}%</div>
          <div className="text-xs opacity-60 mt-2">Adversarial Engine generated</div>
        </div>

        <div className="glass-panel p-4 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Activity size={64} />
          </div>
          <div className="text-sm opacity-70 font-semibold uppercase mb-2 text-yellow-300">Profile Drift (Cosine)</div>
          <div className="text-4xl font-bold font-['Space_Grotesk'] text-cream">{(invData.metrics.driftScore * 100).toFixed(1)}%</div>
          <div className="text-xs opacity-60 mt-2">{invData.metrics.driftScore < 0.3 ? "Stable Identity Pattern" : "ALERT: Pattern Drift Detected"}</div>
        </div>

        <div className="glass-panel p-4 flex flex-col justify-between relative overflow-hidden border-t-2 border-t-purple-500">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Database size={64} />
          </div>
          <div className="text-sm opacity-70 font-semibold uppercase mb-2 text-purple-300">Cross-Referenced Metadata</div>
          <div className="text-4xl font-bold font-['Space_Grotesk'] text-cream">{invData.metrics.metadataHits} Hits</div>
          <div className="text-xs opacity-60 mt-2">EXIF, GPS, Document Attributes</div>
        </div>
      </header>

      {/* 2. MIDDLE ROW: GRAPH & INTELLIGENCE */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[500px]">
        
        {/* Left: Topology Graph */}
        <div className="glass-panel relative overflow-hidden col-span-1 lg:col-span-1">
          <div className="absolute top-4 left-4 z-10 bg-midnight/80 px-4 py-2 rounded-lg border border-white/10 text-sm font-semibold flex items-center gap-2">
            <Network size={16} /> Identity Graph
          </div>
          <ActorGraph initialNodes={invData.graph.nodes} initialEdges={invData.graph.edges} />
        </div>

        {/* Center: Traffic Fingerprinting */}
        <div className="glass-panel p-6 overflow-y-auto flex flex-col gap-6">
          <div className="flex items-center gap-2 border-b border-white/10 pb-2">
            <Wifi className="text-blue-400" size={20} />
            <h2 className="text-xl font-bold font-['Space_Grotesk'] text-cream">Traffic ML Classifier</h2>
          </div>
          
          <div>
            <div className="text-sm opacity-70 mb-1">Deep Fingerprint Prediction</div>
            <div className="text-lg font-bold text-blue-300 bg-blue-950/40 p-3 rounded-lg border border-blue-500/20">
              {invData.traffic.prediction}
            </div>
          </div>

          <div className="space-y-3">
            <div className="text-sm opacity-70">Random Forest Probability Distribution</div>
            {Object.entries(invData.traffic.probabilities).map(([label, prob]) => (
              <div key={label}>
                <div className="flex justify-between text-xs mb-1">
                  <span>{label}</span>
                  <span className="font-mono">{(prob * 100).toFixed(1)}%</span>
                </div>
                <div className="h-2 progress-bar-bg bg-blue-950/30">
                  <div className="progress-bar-fill bg-blue-400" style={{ width: `${prob * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Behavioral Invariants & Metadata */}
        <div className="glass-panel p-6 overflow-y-auto flex flex-col gap-6">
          
          <div className="flex flex-col gap-4 border-b border-white/10 pb-6">
            <div className="flex items-center gap-2 border-b border-white/10 pb-2">
              <User className="text-green-400" size={20} />
              <h2 className="text-xl font-bold font-['Space_Grotesk'] text-cream">Behavioral Invariants</h2>
            </div>
            
            <div className="flex justify-between items-center bg-black/20 p-3 rounded-lg">
              <div>
                <div className="text-xs opacity-70">Hard-to-Fake (Weight: 2.5x)</div>
                <div className="font-semibold text-green-300">Response Latency</div>
              </div>
              <div className="font-mono text-xl">{(invData.behavior.latencyScore * 100).toFixed(0)}%</div>
            </div>
            
            <div className="flex justify-between items-center bg-black/20 p-3 rounded-lg">
              <div>
                <div className="text-xs opacity-70">Easy-to-Fake (Weight: 1.0x)</div>
                <div className="font-semibold text-yellow-300">Active Hours</div>
              </div>
              <div className="font-mono text-xl">{(invData.behavior.activeHoursScore * 100).toFixed(0)}%</div>
            </div>
          </div>

          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 border-b border-white/10 pb-2">
              <FileText className="text-purple-400" size={20} />
              <h2 className="text-xl font-bold font-['Space_Grotesk'] text-cream">Metadata Leaks</h2>
            </div>
            
            {invData.metadata.map((meta, idx) => (
              <div key={idx} className="bg-purple-950/20 p-3 rounded-lg border border-purple-500/20">
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold text-purple-300">{meta.type}</span>
                  <span className="font-mono text-cream">{meta.value}</span>
                </div>
                <div className="text-xs opacity-60 mt-2">Shared by: {meta.personas.join(", ")}</div>
              </div>
            ))}
          </div>

        </div>

      </div>

      {/* 3. BOTTOM ROW: MATHEMATICS & ADVERSARIAL */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        
        {/* Left: Bayesian Fusion Matrix */}
        <div className="glass-panel p-6 border-t-2 border-t-green-500/50">
          <div className="flex items-center gap-2 mb-6 border-b border-white/10 pb-2">
            <BrainCircuit className="text-green-400" size={20} />
            <h2 className="text-xl font-bold font-['Space_Grotesk'] text-cream">Bayesian Evidence Matrix</h2>
          </div>
          
          <div className="space-y-5">
            {invData.evidence_breakdown.map((ev: any, idx: number) => (
              <div key={idx} className="relative">
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold">
                    {ev.name} 
                    <span className="opacity-50 text-xs ml-2">[{ev.group}]</span>
                  </span>
                  <span className="font-mono text-cream flex gap-4">
                    <span className="opacity-50 text-xs text-yellow-200">Reliability Weight: {(ev.reliability).toFixed(2)}</span>
                    <span>{(ev.score).toFixed(2)}</span>
                  </span>
                </div>
                <div className="h-2 progress-bar-bg bg-black/40">
                  <div 
                    className={`h-full rounded-full ${ev.group === 'Network' ? 'bg-blue-400' : ev.group === 'Blockchain' ? 'bg-yellow-400' : 'bg-green-400'}`}
                    style={{ width: `${ev.score * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Adversarial Engine */}
        <div className="glass-panel p-6 border-t-2 border-t-red-500/50 flex flex-col gap-6">
          
          <div className="flex items-center gap-2 border-b border-white/10 pb-2">
            <AlertOctagon className="text-red-400" size={20} />
            <h2 className="text-xl font-bold font-['Space_Grotesk'] text-red-100">Adversarial Engine (Self-Testing)</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-red-950/20 p-4 rounded-xl border border-red-500/20">
              <h3 className="text-sm font-bold uppercase opacity-70 mb-3 text-red-300">Noise Injection (Stress Test)</h3>
              <div className="space-y-3">
                {invData.adversarial_report.stress_test.map((test, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span>Noise ±{(test.noise * 100).toFixed(0)}%</span>
                    <span className="font-mono bg-black/30 px-2 py-1 rounded">Conf: {(test.confidence * 100).toFixed(0)}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-red-950/20 p-4 rounded-xl border border-red-500/20 flex flex-col">
              <h3 className="text-sm font-bold uppercase opacity-70 mb-3 text-red-300">Contradiction Analysis</h3>
              <div className="flex-1 space-y-3">
                {invData.adversarial_report.contradictions.map((contra, idx) => (
                  <div key={idx} className="text-sm text-red-200">
                    <p className="mb-2">{contra.message}</p>
                    <p className="font-mono text-red-400 bg-red-950/50 px-2 py-1 inline-block rounded">Penalty: -{(contra.penalty * 100).toFixed(0)}%</p>
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
