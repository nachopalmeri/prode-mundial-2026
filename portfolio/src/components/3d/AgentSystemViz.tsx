'use client';

import { useRef, useMemo, useState, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html } from '@react-three/drei';
import * as THREE from 'three';

interface AgentNode {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'standby';
  group: number;
}

interface WorkflowEdge {
  from: string;
  to: string;
}

const agentNodes: AgentNode[] = [
  { id: 'principal', name: 'agente-principal', role: 'Lógica, estructura, APIs', status: 'active', group: 0 },
  { id: 'design', name: 'agente-design', role: 'CSS, responsive, animaciones', status: 'active', group: 1 },
  { id: 'web3d', name: 'agente-web-3d', role: 'Three.js, R3F, shaders', status: 'active', group: 1 },
  { id: 'motion', name: 'agente-web-motion', role: 'GSAP, ScrollTrigger, Lenis', status: 'active', group: 1 },
  { id: 'copy', name: 'agente-web-copy', role: 'Copy, CTAs, storytelling', status: 'active', group: 2 },
  { id: 'qa', name: 'agente-web-qa', role: 'Lighthouse, anti-slop, a11y', status: 'active', group: 2 },
  { id: 'marketing', name: 'agente-marketing', role: 'Estrategia, GTM', status: 'standby', group: 3 },
  { id: 'growth', name: 'agente-growth', role: 'SEO/GEO growth', status: 'standby', group: 3 },
  { id: 'security', name: 'agente-security', role: 'Secretos, permisos', status: 'standby', group: 3 },
  { id: 'obsidian', name: 'agente-obsidian', role: 'Obsidian vault, MOCs', status: 'standby', group: 3 },
];

const workflowEdges: WorkflowEdge[] = [
  { from: 'principal', to: 'design' },
  { from: 'principal', to: 'web3d' },
  { from: 'principal', to: 'motion' },
  { from: 'principal', to: 'copy' },
  { from: 'principal', to: 'qa' },
  { from: 'design', to: 'web3d' },
  { from: 'motion', to: 'web3d' },
  { from: 'copy', to: 'qa' },
  { from: 'principal', to: 'marketing' },
  { from: 'marketing', to: 'growth' },
  { from: 'principal', to: 'security' },
  { from: 'principal', to: 'obsidian' },
];

const groupColors = ['#00d9ff', '#22d3ee', '#7c3aed', '#eab308'];

function AgentSphere({ node, position, onSelect, isSelected }: {
  node: AgentNode;
  position: [number, number, number];
  onSelect: (node: AgentNode) => void;
  isSelected: boolean;
}) {
  const ref = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);
  const color = groupColors[node.group];
  const scale = isSelected ? 1.4 : hovered ? 1.2 : 1;

  useFrame((state) => {
    if (ref.current) {
      ref.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 0.5 + position[0]) * 0.1;
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={ref}
        onClick={(e) => { e.stopPropagation(); onSelect(node); }}
        onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
        onPointerOut={() => { setHovered(false); document.body.style.cursor = 'auto'; }}
        scale={scale}
      >
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 0.6 : hovered ? 0.4 : 0.2}
          transparent
          opacity={node.status === 'standby' ? 0.5 : 0.9}
        />
      </mesh>

      {/* Label */}
      <Text
        position={[0, 0.45, 0]}
        fontSize={0.12}
        color={hovered || isSelected ? '#ffffff' : '#9ca3af'}
        anchorX="center"
        anchorY="middle"
        font={undefined}
      >
        {node.name.replace('agente-', '')}
      </Text>

      {/* Status indicator */}
      <mesh position={[0.2, 0.3, 0]}>
        <sphereGeometry args={[0.04, 8, 8]} />
        <meshBasicMaterial color={node.status === 'active' ? '#22c55e' : '#eab308'} />
      </mesh>

      {/* Tooltip on hover */}
      {(hovered || isSelected) && (
        <Html position={[0, -0.4, 0]} center distanceFactor={8} style={{ pointerEvents: 'none' }}>
          <div className="bg-[#0d1117] border border-cyan/30 rounded-md px-3 py-2 text-xs font-mono whitespace-nowrap shadow-lg">
            <div className="text-cyan font-bold">{node.name}</div>
            <div className="text-gray-400">{node.role}</div>
            <div className={`text-[10px] ${node.status === 'active' ? 'text-green-400' : 'text-yellow-400'}`}>
              {node.status}
            </div>
          </div>
        </Html>
      )}
    </group>
  );
}

function WorkflowLines({ positions }: { positions: Record<string, [number, number, number]> }) {
  const ref = useRef<THREE.LineSegments>(null);

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const pos: number[] = [];

    for (const edge of workflowEdges) {
      const from = positions[edge.from];
      const to = positions[edge.to];
      if (from && to) {
        pos.push(from[0], from[1], from[2]);
        pos.push(to[0], to[1], to[2]);
      }
    }

    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    return geo;
  }, [positions]);

  useFrame((state) => {
    if (ref.current) {
      const mat = ref.current.material as THREE.LineBasicMaterial;
      mat.opacity = 0.15 + Math.sin(state.clock.elapsedTime * 0.5) * 0.05;
    }
  });

  return (
    <lineSegments ref={ref} geometry={geometry}>
      <lineBasicMaterial color="#00d9ff" transparent opacity={0.15} />
    </lineSegments>
  );
}

function Scene({ onSelect, selectedNode }: {
  onSelect: (node: AgentNode) => void;
  selectedNode: AgentNode | null;
}) {
  const positions = useMemo<Record<string, [number, number, number]>>(() => {
    const pos: Record<string, [number, number, number]> = {};
    const activeNodes = agentNodes.filter(n => n.status === 'active');
    const standbyNodes = agentNodes.filter(n => n.status === 'standby');

    // Active agents in inner ring
    activeNodes.forEach((node, i) => {
      const angle = (i / activeNodes.length) * Math.PI * 2;
      const radius = 2.5;
      pos[node.id] = [Math.cos(angle) * radius, Math.sin(angle) * 0.8, Math.sin(angle) * radius];
    });

    // Standby agents in outer ring
    standbyNodes.forEach((node, i) => {
      const angle = (i / standbyNodes.length) * Math.PI * 2 + 0.3;
      const radius = 4.5;
      pos[node.id] = [Math.cos(angle) * radius, Math.sin(angle) * 0.4 - 0.5, Math.sin(angle) * radius];
    });

    return pos;
  }, []);

  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[5, 5, 5]} intensity={0.6} color="#00d9ff" />
      <pointLight position={[-5, -5, -5]} intensity={0.3} color="#7c3aed" />

      <WorkflowLines positions={positions} />

      {agentNodes.map((node) => (
        <AgentSphere
          key={node.id}
          node={node}
          position={positions[node.id]}
          onSelect={onSelect}
          isSelected={selectedNode?.id === node.id}
        />
      ))}

      <OrbitControls
        enableZoom={true}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.5}
        minDistance={4}
        maxDistance={12}
        maxPolarAngle={Math.PI / 1.5}
      />
    </>
  );
}

export default function AgentSystemViz() {
  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(null);

  const handleSelect = useCallback((node: AgentNode) => {
    setSelectedNode(prev => prev?.id === node.id ? null : node);
  }, []);

  return (
    <div className="w-full h-[500px] md:h-[600px] relative">
      <Canvas
        camera={{ position: [0, 3, 8], fov: 50 }}
        style={{ background: 'transparent' }}
        gl={{ antialias: true, alpha: true }}
      >
        <Scene onSelect={handleSelect} selectedNode={selectedNode} />
      </Canvas>

      {/* Info panel */}
      {selectedNode && (
        <div className="absolute bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-72 bg-[#0d1117]/90 backdrop-blur-sm border border-cyan/20 rounded-lg p-4 font-mono text-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-cyan font-bold">{selectedNode.name}</span>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-500 hover:text-white text-xs"
            >
              ✕
            </button>
          </div>
          <p className="text-gray-400 text-xs mb-2">{selectedNode.role}</p>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${selectedNode.status === 'active' ? 'bg-green-400' : 'bg-yellow-400'}`} />
            <span className={`text-xs ${selectedNode.status === 'active' ? 'text-green-400' : 'text-yellow-400'}`}>
              {selectedNode.status}
            </span>
          </div>
        </div>
      )}

      {/* Hint */}
      <div className="absolute top-4 right-4 text-[10px] font-mono text-gray-600">
        drag to rotate · click nodes for details
      </div>
    </div>
  );
}
