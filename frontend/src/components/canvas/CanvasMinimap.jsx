import React, { useState } from "react";
import { Compass, Eye, EyeOff } from "lucide-react";

export default function CanvasMinimap({ pan = { x: 0, y: 0 }, setPan, zoom = 0.72 }) {
  const [minimized, setMinimized] = useState(false);

  // Approximate relative bounding coordinates of the workflow canvas
  // Input: (0, 100), M1: (320, 0), M2: (320, 120), M3: (320, 240), M4: (320, 360), M5: (660, 180), Dossier: (960, 180)
  const nodes = [
    { id: "input", x: 10, y: 35, w: 22, h: 28, color: "#ffffff" },
    { id: "m1", x: 40, y: 10, w: 22, h: 18, color: "#adff4f" },
    { id: "m2", x: 40, y: 32, w: 22, h: 18, color: "#38bdf8" },
    { id: "m3", x: 40, y: 54, w: 22, h: 18, color: "#f59e0b" },
    { id: "m4", x: 40, y: 76, w: 22, h: 18, color: "#a855f7" },
    { id: "m5", x: 72, y: 40, w: 24, h: 22, color: "#ec4899" },
    { id: "dossier", x: 104, y: 36, w: 30, h: 30, color: "#adff4f" },
  ];

  // Map main pan/zoom to viewport box inside 140x95 px minimap
  // Canvas width approx 1800, height 1200
  const mapW = 144;
  const mapH = 92;

  // Viewport calculation
  const vpW = Math.max(28, Math.min(mapW, (mapW / zoom) * 0.45));
  const vpH = Math.max(20, Math.min(mapH, (mapH / zoom) * 0.45));
  const vpX = Math.max(0, Math.min(mapW - vpW, mapW / 2 - (pan.x / 14) - vpW / 2));
  const vpY = Math.max(0, Math.min(mapH - vpH, mapH / 2 - (pan.y / 14) - vpH / 2));

  const handleMinimapClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    // Invert coordinate to update pan
    const targetPanX = Math.round((mapW / 2 - clickX) * 14);
    const targetPanY = Math.round((mapH / 2 - clickY) * 14);

    setPan({
      x: Math.max(-800, Math.min(800, targetPanX)),
      y: Math.max(-600, Math.min(600, targetPanY)),
    });
  };

  if (minimized) {
    return (
      <button
        className="minimap-toggle-btn"
        onClick={() => setMinimized(false)}
        title="Open Canvas Radar Navigator"
      >
        <Compass size={14} />
      </button>
    );
  }

  return (
    <div className="canvas-minimap-container">
      <div className="minimap-header">
        <span><Compass size={11} /> CANVAS RADAR</span>
        <button onClick={() => setMinimized(true)} title="Minimize Navigator">
          <EyeOff size={11} />
        </button>
      </div>

      <div className="minimap-viewport" onClick={handleMinimapClick}>
        {/* Render node markers */}
        {nodes.map((n) => (
          <div
            key={n.id}
            className="minimap-node"
            style={{
              left: `${n.x}px`,
              top: `${n.y}px`,
              width: `${n.w}px`,
              height: `${n.h}px`,
              borderColor: n.color,
            }}
          />
        ))}

        {/* Viewport camera frame */}
        <div
          className="minimap-camera-box"
          style={{
            left: `${vpX}px`,
            top: `${vpY}px`,
            width: `${vpW}px`,
            height: `${vpH}px`,
          }}
        />
      </div>
    </div>
  );
}
