"use client";

import { useEffect, useState } from "react";
import { Users, AlertTriangle, ShieldCheck } from "lucide-react";
import Link from "next/link";

interface Cluster {
  id: string;
  title: string;
  confidence: number;
  robustness: number;
  node_count: number;
}

export default function ActorClustersPage() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In production, this points to the real API
    // e.g., fetch("http://localhost:8000/api/v1/clusters/all")
    fetch("http://localhost:8000/api/v1/clusters/all")
      .then((res) => res.json())
      .then((data) => {
        setClusters(data.clusters || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch clusters:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-6 h-full flex flex-col gap-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-4 border-b border-white/10 pb-4">
        <Users className="text-cream" size={32} />
        <div>
          <h1 className="text-3xl font-bold text-cream tracking-tight">Macro Threat Actor Clusters</h1>
          <p className="text-sm text-silver mt-1">Cross-referenced infrastructure & behavioral metadata groups</p>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clusters.map((cluster) => (
            <Link href={`/investigation/${cluster.id}`} key={cluster.id}>
              <div className="clay-card p-6 rounded-xl hover:scale-[1.02] transition-transform cursor-pointer border border-white/5 hover:border-primary/50 relative overflow-hidden group">
                {/* Glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                
                <h2 className="text-xl font-bold text-cream mb-2">{cluster.title}</h2>
                <p className="text-xs text-silver font-mono mb-6">{cluster.id}</p>
                
                <div className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="text-green-400" size={16} />
                    <span className="text-platinum">{(cluster.confidence * 100).toFixed(1)}% Fusion</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertTriangle className={cluster.robustness < 0.5 ? "text-red-400" : "text-yellow-400"} size={16} />
                    <span className="text-platinum">{(cluster.robustness * 100).toFixed(1)}% Robust</span>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-white/10 flex justify-between items-center">
                  <span className="text-xs text-silver">Connected Nodes</span>
                  <span className="text-sm font-bold text-primary">{cluster.node_count}</span>
                </div>
              </div>
            </Link>
          ))}
          {clusters.length === 0 && (
            <div className="col-span-full text-center py-20 text-silver">
              <AlertTriangle size={48} className="mx-auto mb-4 opacity-50" />
              <p>No macro clusters found in Neo4j database.</p>
              <p className="text-sm mt-2">Make sure you ran the data seeder!</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
