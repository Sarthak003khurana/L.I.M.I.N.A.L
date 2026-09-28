import React, { useState } from "react";
import {
  ArrowRight,
  Brain,
  Check,
  Cpu,
  Database,
  FileText,
  FileUp,
  GitBranch,
  Layers3,
  LoaderCircle,
  Network,
  RotateCcw,
  ScanSearch,
  Send,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Zap,
} from "lucide-react";
import { PRESETS } from "../../constants/presets";
import "./InputWorkspace.css";

export default function InputWorkspace({
  text,
  setText,
  loading,
  onInspect,
  pdfLoading,
  pdfInfo,
  handlePdfUpload,
  onClearPdf,
  backendStatus,
  includeAzure,
  setIncludeAzure,
  result,
  onViewPipeline,
}) {
  const [selectedPresetId, setSelectedPresetId] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const isOnline = backendStatus?.online;

  const handleSelectPreset = (preset) => {
    setSelectedPresetId(preset.id);
    setText(preset.text);
    if (pdfInfo) onClearPdf();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.toLowerCase().endsWith(".pdf")) {
        handlePdfUpload(file);
      }
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleLoadSamplePdf = async () => {
    try {
      const res = await fetch("/sample_executive_memo.pdf");
      if (res.ok) {
        const blob = await res.blob();
        const file = new File([blob], "sample_executive_memo.pdf", {
          type: "application/pdf",
        });
        handlePdfUpload(file);
      }
    } catch (e) {
      console.warn("Failed to load sample pdf:", e);
    }
  };

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;

  return (
    <div className="input-workspace">
      {/* Top Banner / Ingestion Header */}
      <div className="iw-header">
        <div className="iw-header-left">
          <div className="iw-stage-badge">
            <span className="iw-stage-dot" />
            <span>STAGE 01 • COMMUNICATION INGESTION</span>
          </div>
          <h1 className="iw-title">Input Communication to Inspect</h1>
          <p className="iw-subtitle">
            Type or paste an email, Slack thread, meeting transcript, or upload an executive PDF.
            Click <strong>Inspect</strong> to launch the 5-agent neural pipeline in this tab.
          </p>
        </div>

        <div className="iw-header-actions">
          {result && onViewPipeline && (
            <button
              type="button"
              className="iw-view-pipeline-btn"
              onClick={onViewPipeline}
              title="Jump to the 5-Model Pipeline Canvas"
            >
              <Network size={14} />
              <span>View Active 5-Model Flow →</span>
            </button>
          )}

          <div className={`iw-status-pill ${isOnline ? "online" : "offline"}`}>
            <i className={isOnline ? "dot-online" : "dot-offline"} />
            <span>{isOnline ? "CUDA 12.8 / RTX 3050 READY" : "CLOUD FALLBACK"}</span>
          </div>
        </div>
      </div>

      {/* Preset Test Scenarios Bar */}
      <div className="iw-presets-bar">
        <div className="iw-presets-label">
          <Sparkles size={13} className="text-cyan" />
          <span>Quick Test Scenarios:</span>
        </div>
        <div className="iw-presets-scroll">
          {PRESETS.map((preset) => (
            <button
              key={preset.id}
              type="button"
              className={`iw-preset-pill ${
                selectedPresetId === preset.id ? "active" : ""
              }`}
              onClick={() => handleSelectPreset(preset)}
              title={preset.description || preset.title}
            >
              <span>{preset.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Dual Grid: Text Area & Document / Options */}
      <div className="iw-grid">
        {/* Left Column: Rich Text Box */}
        <div className="iw-text-card">
          <div className="iw-card-header">
            <div className="iw-card-title">
              <FileText size={15} />
              <span>Communication Payload</span>
            </div>
            <div className="iw-card-meta">
              <span className="iw-count-badge">
                {wordCount} words • {charCount} chars
              </span>
              {text.trim() && (
                <button
                  type="button"
                  className="iw-clear-btn"
                  onClick={() => {
                    setText("");
                    setSelectedPresetId(null);
                    if (pdfInfo) onClearPdf();
                  }}
                  title="Clear text"
                >
                  <RotateCcw size={12} />
                  <span>Clear</span>
                </button>
              )}
            </div>
          </div>

          <div className="iw-textarea-wrapper">
            <textarea
              className="iw-textarea"
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                setSelectedPresetId(null);
              }}
              placeholder="Paste communication to analyze here (e.g. 'I'm fine with whatever you decide. The current plan should probably work. Let's touch base later.')..."
              rows={12}
              autoFocus
            />

            <div className="iw-textarea-footer">
              <div className="iw-tip">
                <span className="tip-badge">FORENSIC SIGNAL</span>
                <span>
                  Hedging words ("probably", "maybe"), passive voice ("was decided"), and deflection trigger rich multi-agent vectors.
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: PDF Ingestion & Pipeline Configuration */}
        <div className="iw-side-column">
          {/* PDF Uploader Card */}
          <div
            className={`iw-pdf-card ${isDragOver ? "dragover" : ""} ${
              pdfInfo ? "has-file" : ""
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="iw-pdf-header">
              <FileUp size={16} className="text-cyan" />
              <span>Executive Document / PDF Ingestion</span>
            </div>

            {pdfInfo ? (
              <div className="iw-pdf-attached">
                <div className="pdf-icon-box">
                  <FileText size={22} />
                </div>
                <div className="pdf-details">
                  <strong className="pdf-filename">{pdfInfo.filename || pdfInfo.name}</strong>
                  <span className="pdf-stats">
                    {pdfInfo.pages} pages • {pdfInfo.characters || text.length} characters extracted
                  </span>
                </div>
                <button
                  type="button"
                  className="pdf-remove-btn"
                  onClick={onClearPdf}
                  title="Remove PDF and keep or clear text"
                >
                  <X size={15} />
                </button>
              </div>
            ) : (
              <div className="iw-pdf-dropzone">
                <div className="dropzone-icon">
                  <Upload size={22} />
                </div>
                <p className="dropzone-text">
                  Drag & drop an executive PDF here, or{" "}
                  <label className="dropzone-browse-label">
                    <span>browse file</span>
                    <input
                      type="file"
                      accept=".pdf"
                      style={{ display: "none" }}
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handlePdfUpload(e.target.files[0]);
                        }
                      }}
                      disabled={pdfLoading}
                    />
                  </label>
                </p>
                <div className="dropzone-actions">
                  <button
                    type="button"
                    className="sample-memo-btn"
                    onClick={handleLoadSamplePdf}
                    disabled={pdfLoading}
                  >
                    <span>Load Sample Executive Memo (PDF)</span>
                  </button>
                </div>
              </div>
            )}

            {pdfLoading && (
              <div className="pdf-loading-overlay">
                <LoaderCircle size={18} className="spin text-cyan" />
                <span>Extracting document text with PyPDF...</span>
              </div>
            )}
          </div>

          {/* 5-Agent Model Pipeline Manifest */}
          <div className="iw-models-card">
            <div className="iw-models-header">
              <Cpu size={15} />
              <span>5-Agent Neural Ensemble to Deploy</span>
            </div>

            <div className="iw-agents-mini-list">
              <div className="agent-mini-item">
                <span className="mini-num">01</span>
                <span className="mini-name">Archaeologist (M1)</span>
                <span className="mini-role">Hedges & Omissions</span>
              </div>
              <div className="agent-mini-item">
                <span className="mini-num">02</span>
                <span className="mini-name">Psychologist (M2)</span>
                <span className="mini-role">Tone & Passive Reluctance</span>
              </div>
              <div className="agent-mini-item">
                <span className="mini-num">03</span>
                <span className="mini-name">Logician (M3)</span>
                <span className="mini-role">Premise & Fallacy Audit</span>
              </div>
              <div className="agent-mini-item">
                <span className="mini-num">04</span>
                <span className="mini-name">Historian (M4)</span>
                <span className="mini-role">FAISS Evidence Grounding</span>
              </div>
              <div className="agent-mini-item">
                <span className="mini-num">05</span>
                <span className="mini-name">Synthesizer (M5)</span>
                <span className="mini-role">Neural Fusion Matrix</span>
              </div>
            </div>

            {/* Azure Explainer Option */}
            <label className="iw-option-toggle">
              <input
                type="checkbox"
                checked={includeAzure}
                onChange={(e) => setIncludeAzure(e.target.checked)}
              />
              <div className="toggle-text">
                <strong>Azure GPT-6 Deep Explainer</strong>
                <small>Generates executive reasoning synthesis and root cause analysis</small>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Sticky Inspection Launcher Bar */}
      <div className="iw-bottom-bar">
        <div className="iw-bottom-info">
          <ShieldCheck size={16} className="text-green" />
          <span>Local CUDA inference • Zero data leakage • Calibrated confidence</span>
        </div>

        <div className="iw-bottom-actions">
          <span className="iw-hotkey-hint">Press [Ctrl + Enter] to Inspect</span>

          <button
            type="button"
            className="iw-inspect-btn"
            disabled={loading || !text.trim()}
            onClick={onInspect}
          >
            {loading ? (
              <>
                <LoaderCircle size={16} className="spin" />
                <span>Deploying Neural Pipeline...</span>
              </>
            ) : (
              <>
                <ScanSearch size={16} />
                <span>Inspect Communication</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
