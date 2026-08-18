import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { Agent, Edge } from "../simulation/types";

type Props = { agents: Agent[]; edges: Edge[]; period: number };

function positionOf(agent: Agent, index: number) {
  const regionBand = [0, 1, -1, 2, -2][["수도권", "충청권", "호남권", "영남권", "강원·제주"].indexOf(agent.region)] ?? 0;
  const incomeHeight = Math.log(Math.max(0.25, agent.income / agent.initialIncome));
  const jitter = Math.sin(index * 12.9898) * 0.42;
  return new THREE.Vector3(
    (agent.resource - 0.5) * 18 + jitter,
    incomeHeight * 8 + (agent.skill - 0.5) * 2.4,
    regionBand * 2.2 + Math.cos(index * 7.13) * 0.55,
  );
}

export function InequalityWorld({ agents, edges, period }: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const meshRef = useRef<THREE.InstancedMesh | null>(null);
  const lineRef = useRef<THREE.LineSegments | null>(null);
  const positions = useMemo(() => agents.map(positionOf), [agents]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#07111f");
    scene.fog = new THREE.FogExp2("#07111f", 0.035);
    const camera = new THREE.PerspectiveCamera(44, host.clientWidth / host.clientHeight, 0.1, 100);
    camera.position.set(14, 9, 20);
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.8));
    renderer.setSize(host.clientWidth, host.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    host.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.minDistance = 11;
    controls.maxDistance = 42;
    controls.target.set(0, 0, 0);

    scene.add(new THREE.AmbientLight("#72a7ff", 1.2));
    const key = new THREE.DirectionalLight("#d5f8ff", 2.5);
    key.position.set(4, 12, 7);
    scene.add(key);

    const grid = new THREE.GridHelper(28, 14, "#1a4965", "#102a41");
    grid.position.y = -4.3;
    scene.add(grid);

    const geometry = new THREE.IcosahedronGeometry(0.16, 1);
    const material = new THREE.MeshStandardMaterial({ roughness: 0.36, metalness: 0.12 });
    const mesh = new THREE.InstancedMesh(geometry, material, agents.length);
    mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    meshRef.current = mesh;
    scene.add(mesh);

    const lineMaterial = new THREE.LineBasicMaterial({ color: "#49b8d3", transparent: true, opacity: 0.1 });
    const lines = new THREE.LineSegments(new THREE.BufferGeometry(), lineMaterial);
    lineRef.current = lines;
    scene.add(lines);

    let frame = 0;
    let raf = 0;
    const animate = () => {
      frame += 0.004;
      controls.update();
      mesh.rotation.y = Math.sin(frame) * 0.025;
      lines.rotation.y = mesh.rotation.y;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(animate);
    };
    animate();

    const resize = () => {
      if (!host.clientWidth || !host.clientHeight) return;
      camera.aspect = host.clientWidth / host.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(host.clientWidth, host.clientHeight);
    };
    const observer = new ResizeObserver(resize);
    observer.observe(host);

    return () => {
      cancelAnimationFrame(raf);
      observer.disconnect();
      controls.dispose();
      geometry.dispose();
      material.dispose();
      lines.geometry.dispose();
      lineMaterial.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      meshRef.current = null;
      lineRef.current = null;
    };
  }, [agents.length]);

  useEffect(() => {
    const mesh = meshRef.current;
    const lines = lineRef.current;
    if (!mesh || !lines) return;
    const matrix = new THREE.Matrix4();
    const color = new THREE.Color();
    agents.forEach((agent, index) => {
      const scale = 0.75 + Math.min(1.5, Math.log1p(agent.capital) * 0.4) + agent.effectiveAI * 0.16;
      matrix.compose(positions[index], new THREE.Quaternion(), new THREE.Vector3(scale, scale, scale));
      mesh.setMatrixAt(index, matrix);
      const change = Math.log(agent.income / agent.initialIncome);
      if (change < -0.02) color.set("#ff6b6b");
      else if (agent.resource < 0.25) color.set("#54e5cb");
      else if (agent.resource > 0.75) color.set("#f6c45b");
      else color.set("#77a8ff");
      color.offsetHSL(0, 0, Math.min(0.18, agent.effectiveAI * 0.05));
      mesh.setColorAt(index, color);
    });
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
    const linePositions = new Float32Array(edges.length * 6);
    edges.forEach((edge, index) => {
      const source = positions[edge.source]; const target = positions[edge.target];
      linePositions.set([source.x, source.y, source.z, target.x, target.y, target.z], index * 6);
    });
    lines.geometry.dispose();
    lines.geometry = new THREE.BufferGeometry();
    lines.geometry.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
  }, [agents, edges, positions, period]);

  return <div className="world" ref={hostRef} role="img" aria-label="소득·자원·지역에 따른 3차원 에이전트 네트워크" />;
}
