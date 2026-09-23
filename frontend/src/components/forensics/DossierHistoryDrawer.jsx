import React, { useState, useEffect } from "react";
import { X, Search, Trash2, RotateCcw, Download, Clock, ShieldCheck, FileText } from "lucide-react";

export default function DossierHistoryDrawer({ isOpen, onClose, onSelectCase }) {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = () => {
    try {
      const raw = localStorage.getItem("liminal_cases");
      if (raw) {
        setHistory(JSON.parse(raw));
      } else {
        setHistory([]);
      }
    } catch (e) {
      console.error("Failed to load cases from localStorage:", e);
      setHistory([]);
    }
  };

  const deleteCase = (id, e) => {
    e.stopPropagation();
    const updated = history.filter((item) => item.id !== id);
    setHistory(updated);
    try {
      localStorage.setItem("liminal_cases", JSON.stringify(updated));
    } catch (err) {
      console.error(err);
    }
  };

  const clearAll = () => {
    if (window.confirm("Clear all historical forensic dossiers?")) {
      setHistory([]);
      try {
        localStorage.removeItem("liminal_cases");
      } catch (err) {
        console.error(err);
      }
    }
  };

  const exportAllJSON = () => {
    const blob = new Blob([JSON.stringify(history, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `liminal_case_archive_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filtered = history.filter((item) => {
    const q = search.toLowerCase();
    return (
      item.text?.toLowerCase().includes(q) ||
      item.pattern?.toLowerCase().includes(q) ||
      item.subtext?.toLowerCase().includes(q)
    );
  });

  if (!isOpen) return null;

  return (
    <div className="history-drawer-backdrop" onClick={onClose}>
      <aside className="history-drawer-panel" onClick={(e) => e.stopPropagation()}>
        <header className="history-drawer-header">
          <div className="drawer-title-group">
            <FileText size={16} className="drawer-icon" />
            <div>
              <h3>FORENSIC CASE ARCHIVE</h3>
              <small>{history.length} SAVED CASE DOSSIERS</small>
            </div>
          </div>
          <button className="drawer-close-btn" onClick={onClose} title="Close drawer (Esc)">
            <X size={16} />
          </button>
        </header>

        <div className="drawer-search-bar">
          <Search size={14} className="search-icon" />
          <input
            type="text"
            placeholder="Filter by keyword, pattern or subtext..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="drawer-actions-strip">
          <button className="strip-btn" onClick={exportAllJSON} disabled={history.length === 0}>
            <Download size={12} />
            EXPORT ALL JSON
          </button>
          <button className="strip-btn danger" onClick={clearAll} disabled={history.length === 0}>
            <Trash2 size={12} />
            CLEAR ARCHIVE
          </button>
        </div>

        <div className="history-list">
          {filtered.length === 0 ? (
            <div className="empty-history">
              <ShieldCheck size={28} className="empty-icon" />
              <p>No forensic dossiers saved yet.</p>
              <small>Run any communication sample in the studio to automatically persist cases.</small>
            </div>
          ) : (
            filtered.map((item) => (
              <div
                key={item.id}
                className="case-card"
                onClick={() => {
                  onSelectCase(item);
                  onClose();
                }}
              >
                <div className="case-card-header">
                  <span className="case-pattern-tag">{item.pattern || "FORENSIC CASE"}</span>
                  <span className="case-confidence">
                    {Math.round(item.confidence || 97)}% CONF
                  </span>
                  <button
                    className="case-delete-btn"
                    onClick={(e) => deleteCase(item.id, e)}
                    title="Delete case"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>

                <p className="case-snippet">"{item.text}"</p>

                {item.subtext && <p className="case-subtext-note">{item.subtext}</p>}

                <div className="case-meta">
                  <span>
                    <Clock size={11} />
                    {new Date(item.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <span className="restore-hint">Click to load into Canvas →</span>
                </div>
              </div>
            ))
          )}
        </div>
      </aside>
    </div>
  );
}
