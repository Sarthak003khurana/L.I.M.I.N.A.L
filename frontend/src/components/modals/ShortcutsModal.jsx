import React from "react";
import { X, Command, Keyboard } from "lucide-react";

export default function ShortcutsModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const shortcuts = [
    { keys: ["Ctrl / ⌘", "Enter"], label: "Run Multi-Agent Pipeline", desc: "Trigger parallel inference across all 5 models" },
    { keys: ["0"], label: "Inspect Input Node", desc: "Select and view message payload editor" },
    { keys: ["1"], label: "Inspect M1 Archaeologist", desc: "Examine syntactic hedging & omission probabilities" },
    { keys: ["2"], label: "Inspect M2 Psychologist", desc: "Analyze affective tone and evasion metrics" },
    { keys: ["3"], label: "Inspect M3 Logician", desc: "Review structural premise & argument continuity" },
    { keys: ["4"], label: "Inspect M4 Historian", desc: "Query FAISS vector precedent matches" },
    { keys: ["5"], label: "Inspect M5 Synthesizer", desc: "Inspect neural feature fusion & weights" },
    { keys: ["D"], label: "Inspect Subtext Dossier", desc: "View full findings, radar chart, & Azure explanation" },
    { keys: ["H"], label: "Toggle Case Archive", desc: "Open the saved forensic case history drawer" },
    { keys: ["R"], label: "Reset Canvas View", desc: "Center graph at standard 72% zoom level" },
    { keys: ["?"], label: "Keyboard Shortcuts", desc: "Open this forensic shortcuts reference" },
    { keys: ["Esc"], label: "Dismiss / Close", desc: "Close any open modal or history drawer" },
  ];

  return (
    <div className="shortcuts-modal-backdrop" onClick={onClose}>
      <div className="shortcuts-modal-panel" onClick={(e) => e.stopPropagation()}>
        <header className="shortcuts-modal-header">
          <div className="shortcuts-title-group">
            <Keyboard size={18} className="shortcuts-icon" />
            <div>
              <h3>ANALYST KEYBOARD SHORTCUTS</h3>
              <small>L.I.M.I.N.A.L. OPERATIONAL COMMANDS</small>
            </div>
          </div>
          <button className="shortcuts-close-btn" onClick={onClose} title="Close (Esc)">
            <X size={16} />
          </button>
        </header>

        <div className="shortcuts-list">
          {shortcuts.map((sc, i) => (
            <div key={i} className="shortcut-row">
              <div className="shortcut-keys">
                {sc.keys.map((k, kIdx) => (
                  <kbd key={kIdx} className="key-cap">{k}</kbd>
                ))}
              </div>
              <div className="shortcut-info">
                <strong>{sc.label}</strong>
                <p>{sc.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <footer className="shortcuts-footer">
          <span>Tip: Press <kbd className="key-cap inline">?</kbd> at any time to summon this HUD</span>
        </footer>
      </div>
    </div>
  );
}
