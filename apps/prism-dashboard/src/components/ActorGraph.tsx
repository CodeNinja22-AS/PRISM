"use client";

import React, { useCallback } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  addEdge,
  Background,
  Controls,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// A custom node style to fit the Cyber-Clay-Glass aesthetic
const nodeStyles = {
  background: 'var(--color-glass-bg)',
  backdropFilter: 'blur(10px)',
  border: '1px solid var(--color-glass-border)',
  borderRadius: '50%', // Orb shape
  padding: '15px',
  color: 'var(--color-platinum)',
  width: 100,
  height: 100,
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  textAlign: 'center' as const,
  fontSize: '12px',
  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3), inset 0 2px 4px rgba(255,255,255,0.1)'
};

const actorNodeStyle = {
  ...nodeStyles,
  background: 'var(--color-cream)',
  color: 'var(--color-midnight)',
  boxShadow: '8px 8px 16px rgba(0,0,0,0.4), inset 2px 2px 4px rgba(255,255,255,0.8), inset -2px -2px 4px rgba(0,0,0,0.2)',
  fontWeight: 'bold'
};

const alertNodeStyle = {
  ...nodeStyles,
  border: '2px solid #ef4444',
  boxShadow: '0 0 15px rgba(239, 68, 68, 0.5)'
};

export default function ActorGraph({ initialNodes, initialEdges }: { initialNodes: any[], initialEdges: any[] }) {
  // Map API data to React Flow structure
  const formattedNodes = initialNodes.map((n, i) => {
    let style = nodeStyles;
    if (n.data.type === "ActorCluster" || n.data.type === "Persona") {
      style = actorNodeStyle;
    } else if (n.data.alert) {
      style = alertNodeStyle;
    }
    
    return {
      id: n.id,
      position: { x: (i % 3) * 150 + 50, y: Math.floor(i / 3) * 150 + 50 }, // simple grid layout
      data: { label: n.data.label },
      style
    };
  });

  const formattedEdges = initialEdges.map(e => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label,
    style: { stroke: 'var(--color-platinum)', opacity: 0.5 },
    labelStyle: { fill: 'var(--color-platinum)', fontSize: 10 },
    labelBgStyle: { fill: 'var(--color-midnight)' },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: 'var(--color-platinum)',
    },
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(formattedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(formattedEdges);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background color="#ccc" gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
