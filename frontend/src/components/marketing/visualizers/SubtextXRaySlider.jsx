import { useState, useRef } from "react";
import { ShieldAlert, ShieldCheck, Sparkles } from "lucide-react";
import "./SubtextXRaySlider.css";

export default function SubtextXRaySlider() {
  const [sliderPos, setSliderPos] = useState(50);
  const containerRef = useRef(null);
  const isDragging = useRef(false);

  const updatePosition = (clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPos(percent);
  };

  const handlePointerDown = (e) => {
    isDragging.current = true;
    try {
      e.currentTarget.setPointerCapture(e.pointerId);
    } catch {
      /* ignore */
    }
    updatePosition(e.clientX);
  };

  const handlePointerUp = (e) => {
    isDragging.current = false;
    try {
      e.currentTarget.releasePointerCapture(e.pointerId);
    } catch {
      /* ignore */
    }
  };

  const handlePointerMove = (e) => {
    if (!isDragging.current) return;
    updatePosition(e.clientX);
  };

  return (
    <div
      className="xray-container"
      ref={containerRef}
      onPointerDown={handlePointerDown}
      onPointerUp={handlePointerUp}
      onPointerMove={handlePointerMove}
    >
      {/* Top HUD bar */}
      <div className="xray-hud-header">
        <div className="xray-hud-title">
          <span className="xray-dot" />
          <span>DUAL-LENS FORENSIC COMPARISON SLIDER</span>
        </div>
        <div className="xray-hud-hint">DRAG LASER SCANLINE TO REVEAL SUBTEXT</div>
      </div>

      <div className="xray-display-wrapper">
        {/* RIGHT LAYER: LIMINAL SUBTEXT SCANNER (Underneath) */}
        <div className="xray-layer xray-layer-liminal">
          <div className="xray-badge badge-liminal">
            <ShieldAlert size={13} />
            <span>L.I.M.I.N.A.L. FORENSIC RADAR</span>
          </div>

          <div className="xray-quote">
            “We remain{" "}
            <span className="hl-hedge" title="M1: Hedging Softener">
              largely confident
            </span>{" "}
            that key deliverables{" "}
            <span className="hl-passive" title="M1: Passive Deflection">
              will be finalized
            </span>{" "}
            once broader team alignment{" "}
            <span className="hl-omission" title="M3: Missing Actor & Criteria">
              is achieved
            </span>
            .”
          </div>

          <div className="xray-findings-grid">
            <div className="finding-pill amber">
              <strong>M1 ARCHAEOLOGIST</strong>
              <span>Agentless passive deflection + zero commit date</span>
            </div>
            <div className="finding-pill red">
              <strong>M2 PSYCHOLOGIST</strong>
              <span>Affect dampening & evasive distance (p=0.96)</span>
            </div>
            <div className="finding-pill purple">
              <strong>M3 LOGICIAN</strong>
              <span>Unstated premise: Alignment condition is non-deterministic</span>
            </div>
            <div className="finding-pill green">
              <strong>M5 SYNTHESIZER</strong>
              <span>Pattern: STRATEGIC_DELAY (94.2% Conf.)</span>
            </div>
          </div>
        </div>

        {/* LEFT LAYER: STANDARD NLP (Clipped by sliderPos) */}
        <div
          className="xray-layer xray-layer-standard"
          style={{ clipPath: `inset(0 ${100 - sliderPos}% 0 0)` }}
        >
          <div className="xray-badge badge-standard">
            <ShieldCheck size={13} />
            <span>STANDARD NLP & SENTIMENT ENGINE</span>
          </div>

          <div className="xray-quote standard-quote">
            “We remain{" "}
            <span className="hl-plain">
              largely confident
            </span>{" "}
            that key deliverables{" "}
            <span className="hl-plain">
              will be finalized
            </span>{" "}
            once broader team alignment{" "}
            <span className="hl-plain">
              is achieved
            </span>
            .”
          </div>

          <div className="standard-verdict">
            <div className="standard-verdict-row">
              <span className="standard-label">Sentiment:</span>
              <span className="standard-val positive">Positive / Constructive (91.4%)</span>
            </div>
            <div className="standard-verdict-row">
              <span className="standard-label">Intent:</span>
              <span className="standard-val">Progress Status Update</span>
            </div>
            <div className="standard-verdict-row">
              <span className="standard-label">Presence Bias:</span>
              <span className="standard-val warning">Blind to missing deadlines & omitted ownership</span>
            </div>
          </div>
        </div>

        {/* DRAGGABLE DIVIDER LINE */}
        <div
          className="xray-slider-line"
          style={{ left: `${sliderPos}%` }}
        >
          <div className="xray-slider-handle">
            <div className="handle-bar" />
            <div className="handle-bar" />
          </div>
        </div>
      </div>
    </div>
  );
}
