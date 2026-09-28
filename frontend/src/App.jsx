import { useEffect, useRef, useState, useCallback } from "react";
import {
  Activity,
  ArrowUpRight,
  Brain,
  Check,
  ChevronRight,
  ClipboardList,
  Copy,
  Database,
  Download,
  ExternalLink,
  FileText,
  FileUp,
  GitBranch,
  Globe,
  History,
  Keyboard,
  Layers3,
  LoaderCircle,
  Lock,
  LogOut,
  Network,
  Play,
  RotateCcw,
  ScanSearch,
  Send,
  Settings2,
  ShieldCheck,
  Sparkles,
  Upload,
  User,
  Workflow,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";

import LandingPage from "./components/marketing/LandingPage";
import LoginPage from "./components/auth/LoginPage";
import AnalysisPage from "./components/forensics/AnalysisPage";
import ForensicHighlighter from "./components/forensics/ForensicHighlighter";
import ForensicRadarChart from "./components/forensics/ForensicRadarChart";
import DossierHistoryDrawer from "./components/forensics/DossierHistoryDrawer";
import CanvasMinimap from "./components/canvas/CanvasMinimap";
import ShortcutsModal from "./components/modals/ShortcutsModal";
import ModelTelemetryModal from "./components/modals/ModelTelemetryModal";
import InputWorkspace from "./components/workspace/InputWorkspace";
import { logOutFirebase } from "./firebase/config";
import { PRESETS } from "./constants/presets";
import { computeForensicMetrics } from "./utils/forensicsMetrics";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SAMPLE_TEXT =
  "I'm fine with whatever you decide. The current plan should probably work.";

const STAGES = [
  "input",
  "archaeologist",
  "psychologist",
  "logician",
  "historian",
  "synthesizer",
  "dossier",
];

const AGENTS = {
  archaeologist: {
    number: "01",
    name: "Archaeologist",
    subtitle: "Archaeologist Agent",
    icon: ScanSearch,
    color: "green",
    description:
      "Linguistic Forensics: Detects hedging, omissions, passive constructions and responsibility gaps.",
    meta: ["Transformer", "326 vocab", "7 labels"],
    x: 365,
    y: 390,
  },

  psychologist: {
    number: "02",
    name: "Psychologist",
    subtitle: "Psychologist Agent",
    icon: Brain,
    color: "violet",
    description:
      "Affect & Interpersonal: Looks for affect gaps, disengagement and interpersonal communication signals.",
    meta: ["Transformer", "216 vocab", "7 labels"],
    x: 705,
    y: 55,
  },

  logician: {
    number: "03",
    name: "Logician",
    subtitle: "Logician Agent",
    icon: GitBranch,
    color: "blue",
    description:
      "Reasoning Analysis: Checks premises, assumptions, contradictions and unsupported conclusions.",
    meta: ["Transformer", "466 vocab", "6 labels"],
    x: 705,
    y: 390,
  },

  historian: {
    number: "04",
    name: "Historian",
    subtitle: "Historian Agent",
    icon: Database,
    color: "amber",
    description:
      "Evidence Retrieval: Retrieves relevant linguistic and reasoning evidence from the knowledge base.",
    meta: ["FAISS", "TF-IDF", "18 records"],
    x: 705,
    y: 725,
  },

  synthesizer: {
    number: "05",
    name: "Synthesizer",
    subtitle: "Synthesizer Agent",
    icon: Network,
    color: "green",
    description:
      "Cross-Agent Fusion: Combines upstream analyses into a calibrated subtext prediction.",
    meta: ["52,459 params", "25 features", "8 labels"],
    x: 1050,
    y: 390,
  },
};

export default function App() {
  const getInitialView = () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const v = params.get("view");
      if (v === "studio" || v === "login" || v === "analysis") {
        return v;
      }
    } catch {
      /* ignore view parse error */
    }
    return "landing";
  };

  const getInitialText = () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const urlText = params.get("text");
      if (urlText) {
        return decodeURIComponent(urlText);
      }
      const pending = sessionStorage.getItem("liminal_pending_text");
      if (pending) {
        sessionStorage.removeItem("liminal_pending_text");
        return pending;
      }
    } catch {
      /* ignore text parse error */
    }
    return SAMPLE_TEXT;
  };

  const [text, setText] = useState(getInitialText);
  const [result, setResult] = useState(null);

  const [stage, setStage] = useState("dossier");
  const [selected, setSelected] = useState("dossier");
  const [view, setViewState] = useState(getInitialView);
  const [studioMode, setStudioMode] = useState("input"); // "input" | "pipeline"
  const [isDragging, setIsDragging] = useState(false);

  const [currentUser, setCurrentUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("liminal_user") || "null");
    } catch {
      return null;
    }
  });

  const handleInspect = () => {
    if (!text.trim()) return;
    setStudioMode("pipeline");
    setTimeout(() => {
      analyze();
    }, 120);
  };

  const handleLogout = async () => {
    try {
      await logOutFirebase();
    } catch (e) {
      console.warn("Firebase logout warning:", e);
    }
    try {
      localStorage.removeItem("liminal_authenticated");
      localStorage.removeItem("liminal_user");
      sessionStorage.clear();
    } catch {
      /* ignore storage clear error */
    }
    setCurrentUser(null);
    setView("login");
  };

  const setView = (newView, replace = false) => {
    setViewState(newView);
    try {
      const url = new URL(window.location.href);
      if (newView === "landing") {
        url.searchParams.delete("view");
      } else {
        url.searchParams.set("view", newView);
      }
      if (replace) {
        window.history.replaceState(null, "", url.toString());
      } else {
        window.history.pushState(null, "", url.toString());
      }
    } catch {
      /* ignore navigation error */
    }
  };

  useEffect(() => {
    const handlePopState = () => {
      try {
        const params = new URLSearchParams(window.location.search);
        const v = params.get("view") || "landing";
        setViewState(v);
      } catch {
        /* ignore popstate parse error */
      }
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const [includeAzure, setIncludeAzure] = useState(true);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Upgraded Forensics & Workflow States
  const [isInspectorOpen, setIsInspectorOpen] = useState(false); // Collapsed by default for a clean, spacious canvas
  const [isInputModalOpen, setIsInputModalOpen] = useState(false); // Floating hover box for text input
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);
  const [inputViewMode, setInputViewMode] = useState("edit"); // "edit" | "forensics"
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfInfo, setPdfInfo] = useState(null);
  const [remediations, setRemediations] = useState(null);
  const [remediating, setRemediating] = useState(false);
  const [telemetryModal, setTelemetryModal] = useState(null); // { agentId, tab }

  const openTelemetry = (agentId, tab = "labels") => {
    setTelemetryModal({ agentId, tab });
  };

  const [backendStatus, setBackendStatus] = useState({
    online: false,
    loading: true,
    device: "cuda",
    azure_explainer: "checking",
  });

  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        setBackendStatus({
          online: data.status === "healthy" || data.status === "online",
          loading: data.status === "loading",
          device: data.device || "cuda",
          azure_explainer: data.azure_explainer || "not_loaded",
        });
      } else {
        setBackendStatus((s) => ({ ...s, online: false, loading: false }));
      }
    } catch {
      setBackendStatus((s) => ({ ...s, online: false, loading: false }));
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      checkHealth();
    }, 0);
    const interval = setInterval(checkHealth, 15000);
    return () => {
      clearTimeout(timer);
      clearInterval(interval);
    };
  }, [checkHealth]);

  const [zoom, setZoom] = useState(0.76);

  const [pan, setPan] = useState({
    x: 15,
    y: -10,
  });

  const [elapsed, setElapsed] = useState(0);

  const dragging = useRef(false);

  const dragStart = useRef({
    x: 0,
    y: 0,
  });

  const panStart = useRef({
    x: 0,
    y: 0,
  });

  const stageIndex = STAGES.indexOf(stage);

  const resetCanvas = () => {
    setZoom(0.76);

    setPan({
      x: 15,
      y: -10,
    });
  };

  // Case Archive Persistence
  const saveCaseToHistory = (cleanText, resultData) => {
    try {
      const raw = localStorage.getItem("liminal_cases");
      const list = raw ? JSON.parse(raw) : [];
      const newCase = {
        id: `case_${Date.now()}`,
        timestamp: new Date().toISOString(),
        text: cleanText,
        pattern: resultData?.dossier?.primary_pattern || resultData?.agents?.synthesizer?.prediction || "UNSTATED_PREFERENCE",
        confidence: getConfidence(resultData),
        subtext: resultData?.dossier?.possible_subtext || "",
        missing: resultData?.dossier?.strategically_missing || [],
        result: resultData,
      };
      const updated = [newCase, ...list.filter((c) => c.text !== cleanText)].slice(0, 30);
      localStorage.setItem("liminal_cases", JSON.stringify(updated));
    } catch (err) {
      console.error("Failed to save case to history:", err);
    }
  };

  const analyze = useCallback(
    async (overrideText) => {
      const textToAnalyze =
        typeof overrideText === "string" ? overrideText : text;
      const cleanText = textToAnalyze.trim();

      if (!cleanText) {
        setError("Enter a communication sample first.");
        return;
      }

      setError("");
      setResult(null);
      setLoading(true);
      setElapsed(0);
      setStage("input");

      const started = performance.now();

      const timer = setInterval(() => {
        setElapsed((performance.now() - started) / 1000);
      }, 100);

      try {
        // Use real-time Server-Sent Events stream
        const response = await fetch(`${API_URL}/analyze/stream`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: cleanText,
            include_azure: includeAzure,
          }),
        });

        if (!response.ok) {
          let detail = `Backend returned status ${response.status}`;
          try {
            const errPayload = await response.json();
            if (errPayload?.detail) {
              detail =
                typeof errPayload.detail === "string"
                  ? errPayload.detail
                  : JSON.stringify(errPayload.detail);
            }
          } catch {
            /* ignore error parse failure */
          }
          throw new Error(detail);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop();

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data: ")) continue;
            try {
              const eventData = JSON.parse(trimmed.slice(6));
              if (eventData.event === "agent_complete") {
                setStage(eventData.agent);
                if (eventData.data) {
                  setResult((prev) => ({
                    ...(prev || {}),
                    agents: {
                      ...(prev?.agents || {}),
                      [eventData.agent]: eventData.data,
                    },
                  }));
                }
              } else if (eventData.event === "azure_start") {
                setStage("synthesizer");
              } else if (eventData.event === "done") {
                setResult(eventData.result);
                setStage("dossier");
                setSelected("dossier");
                saveCaseToHistory(cleanText, eventData.result);
                // Smooth transition to dedicated full-page forensic analysis
                setView("analysis");
              }
            } catch (e) {
              console.error("SSE line parse error:", e);
            }
          }
        }

        checkHealth();
      } catch (err) {
        console.error(err);

        setError(
          err.message?.includes("Backend returned") ||
            err.message?.includes("failed") ||
            err.message?.includes("models")
            ? err.message
            : "Backend connection failed. Make sure FastAPI is running on http://localhost:8000."
        );

        setStage("input");
      } finally {
        clearInterval(timer);

        setElapsed((performance.now() - started) / 1000);

        setLoading(false);
      }
    },
    [text, includeAzure, checkHealth]
  );

  // Subtext Remediation Engine
  const handleRemediate = async () => {
    if (!text.trim()) return;
    setRemediating(true);
    try {
      const resp = await fetch(`${API_URL}/remediate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text.trim(),
          dossier: result?.dossier || null,
        }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setRemediations(data);
      }
    } catch (err) {
      console.error("Remediation error:", err);
    } finally {
      setRemediating(false);
    }
  };

  const handleApplyRemediation = (rewrittenText) => {
    setText(rewrittenText);
    setRemediations(null);
    setInputViewMode("edit");
    // Trigger instant re-analysis
    setTimeout(() => {
      analyze(rewrittenText);
    }, 100);
  };

  // PDF Document Forensics
  const handlePdfUpload = async (file) => {
    if (!file) return;
    setPdfLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const resp = await fetch(`${API_URL}/extract-pdf`, {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "Failed to extract PDF");
      }
      const data = await resp.json();
      setText(data.text);
      setPdfInfo({
        filename: data.filename,
        pages: data.pages,
        characters: data.characters,
      });
      setSelected("input");
    } catch (err) {
      setError(`PDF error: ${err.message}`);
    } finally {
      setPdfLoading(false);
    }
  };

  const onClearPdf = () => {
    setPdfInfo(null);
  };

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      const isEditing = ["TEXTAREA", "INPUT"].includes(e.target.tagName);
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        analyze();
        return;
      }
      if (e.key === "Escape") {
        setIsHistoryOpen(false);
        setIsShortcutsOpen(false);
        return;
      }
      if (isEditing) return;

      if (e.key === "?") {
        setIsShortcutsOpen((v) => !v);
      } else if (e.key === "h" || e.key === "H") {
        setIsHistoryOpen((v) => !v);
      } else if (e.key === "a" || e.key === "A") {
        if (result) setView("analysis");
      } else if (e.key === "s" || e.key === "S") {
        setView("studio");
      } else if (e.key === "l" || e.key === "L") {
        setView("landing");
      } else if (e.key === "0") {
        setSelected("input");
      } else if (e.key === "1") {
        setSelected("archaeologist");
      } else if (e.key === "2") {
        setSelected("psychologist");
      } else if (e.key === "3") {
        setSelected("logician");
      } else if (e.key === "4") {
        setSelected("historian");
      } else if (e.key === "5") {
        setSelected("synthesizer");
      } else if (e.key === "6" || e.key === "d" || e.key === "D") {
        setSelected("dossier");
      } else if (e.key === "i" || e.key === "I") {
        setIsInspectorOpen((prev) => !prev);
      } else if (e.key === "r" || e.key === "R") {
        resetCanvas();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [analyze, result]);

  const pointerDown = (event) => {
    if (event.button !== 0) return;

    if (
      event.target.closest(
        "button, textarea, input"
      )
    ) {
      return;
    }

    dragging.current = true;
    setIsDragging(true);

    dragStart.current = {
      x: event.clientX,
      y: event.clientY,
    };

    panStart.current = {
      ...pan,
    };
  };

  const pointerMove = (event) => {
    if (!dragging.current) return;

    const dx =
      event.clientX -
      dragStart.current.x;

    const dy =
      event.clientY -
      dragStart.current.y;

    setPan({
      x: Math.round(panStart.current.x + dx),
      y: Math.round(panStart.current.y + dy),
    });
  };

  const pointerUp = () => {
    dragging.current = false;
    setIsDragging(false);
  };

  const wheel = (event) => {
    event.preventDefault();

    setZoom((value) => {
      const next =
        value +
        (event.deltaY < 0 ? 0.04 : -0.04);

      return Math.max(
        0.62,
        Math.min(0.9, Number(next.toFixed(2)))
      );
    });
  };

  const selectedAgent =
    selected in AGENTS
      ? AGENTS[selected]
      : null;

  if (view === "landing") {
    return (
      <LandingPage
        onNavigateLogin={() => {
          const query = new URLSearchParams();
          query.set("view", "login");
          const targetUrl = `${window.location.origin}${window.location.pathname}?${query.toString()}`;
          window.open(targetUrl, "_blank");
        }}
        onLaunchStudio={(initialText) => {
          if (initialText) {
            try {
              sessionStorage.setItem("liminal_pending_text", initialText);
            } catch {
              /* ignore storage error */
            }
          }
          const query = new URLSearchParams();
          query.set("view", isAuth ? "studio" : "login");
          if (initialText) query.set("text", initialText);
          const targetUrl = `${window.location.origin}${window.location.pathname}?${query.toString()}`;
          window.open(targetUrl, "_blank");
        }}
        backendStatus={backendStatus}
        currentUser={currentUser}
        onLogout={handleLogout}
      />
    );
  }

  const isAuth =
    typeof window !== "undefined" &&
    localStorage.getItem("liminal_authenticated") === "true";

  if (view === "login" || (!isAuth && view === "studio")) {
    return (
      <LoginPage
        onLogin={(loggedUser) => {
          if (loggedUser) {
            setCurrentUser(loggedUser);
          } else {
            try {
              setCurrentUser(
                JSON.parse(localStorage.getItem("liminal_user") || "null")
              );
            } catch {
              /* ignore parse error */
            }
          }
          setStudioMode("input");
          setView("studio");
        }}
        onBackToLanding={() => {
          setView("landing");
        }}
        backendStatus={backendStatus}
      />
    );
  }

  if (view === "analysis") {
    return (
      <AnalysisPage
        result={result}
        text={text}
        onBackToStudio={() => setView("studio")}
        onNavigateLanding={() => setView("landing")}
        onReAnalyze={() => {
          setView("studio");
          setTimeout(() => {
            analyze();
          }, 150);
        }}
        loading={loading}
        backendStatus={backendStatus}
        remediations={remediations}
        remediating={remediating}
        handleRemediate={handleRemediate}
        handleApplyRemediation={handleApplyRemediation}
      />
    );
  }

  return (
    <div className="app-shell">
      <Sidebar
        selected={selected}
        setSelected={setSelected}
        backendStatus={backendStatus}
        view={view}
        setView={setView}
        result={result}
        onOpenHistory={() => setIsHistoryOpen(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
        studioMode={studioMode}
        setStudioMode={setStudioMode}
      />

      <main className="main-shell">
        <Topbar
          resetCanvas={resetCanvas}
          loading={loading}
          backendStatus={backendStatus}
          onOpenShortcuts={() => setIsShortcutsOpen(true)}
          isInspectorOpen={isInspectorOpen}
          setIsInspectorOpen={setIsInspectorOpen}
          studioMode={studioMode}
        />

        {studioMode === "input" ? (
          <InputWorkspace
            text={text}
            setText={setText}
            loading={loading}
            onInspect={handleInspect}
            pdfLoading={pdfLoading}
            pdfInfo={pdfInfo}
            handlePdfUpload={handlePdfUpload}
            onClearPdf={onClearPdf}
            backendStatus={backendStatus}
            includeAzure={includeAzure}
            setIncludeAzure={setIncludeAzure}
            result={result}
            onViewPipeline={() => setStudioMode("pipeline")}
          />
        ) : (
          <>
            <section
              className={`canvas ${
                isDragging ? "dragging" : ""
              }`}
              onPointerDown={pointerDown}
              onPointerMove={pointerMove}
              onPointerUp={pointerUp}
              onPointerCancel={pointerUp}
              onPointerLeave={pointerUp}
              onWheel={wheel}
            >
          <div className="canvas-grid" />

          <CanvasHeader />

          <div
            className="workflow-world"
            style={{
              transform: `translate3d(${pan.x}px, ${pan.y}px, 0) scale(${zoom})`,
            }}
          >
            <WorkflowEdges
              stageIndex={stageIndex}
              loading={loading}
            />

            <InputNode
              text={text}
              setText={setText}
              loading={loading}
              selected={selected === "input"}
              onSelect={() => setSelected("input")}
              analyze={analyze}
              onOpenInputModal={() => setStudioMode("input")}
              onEditInput={() => setStudioMode("input")}
            />

            {Object.entries(AGENTS).map(
              ([id, agent]) => (
                <AgentNode
                  key={id}
                  id={id}
                  agent={agent}
                  stage={stage}
                  result={result}
                  text={text}
                  loading={loading}
                  selected={selected === id}
                  onSelect={() =>
                    setSelected(id)
                  }
                  onOpenTelemetry={(tab) =>
                    openTelemetry(id, tab)
                  }
                />
              )
            )}

            <Evidence
              visible={
                stageIndex >= 4 ||
                Boolean(result)
              }
              result={result}
            />

            <DossierNode
              result={result}
              stage={stage}
              selected={
                selected === "dossier"
              }
              onSelect={() =>
                setSelected("dossier")
              }
              onOpenFullAnalysis={() => setView("analysis")}
            />
          </div>

          <CanvasControls
            zoom={zoom}
            setZoom={setZoom}
            resetCanvas={resetCanvas}
          />

          <CanvasMinimap
            pan={pan}
            setPan={setPan}
            zoom={zoom}
          />

          <div className="canvas-hint">
            <span>✥</span>
            Drag canvas to navigate • Press [?] for shortcuts • [I] for Inspector
          </div>
        </section>

        <BottomBar
          loading={loading}
          stage={stage}
          result={result}
          elapsed={elapsed}
        />
        </>
        )}
      </main>

      {studioMode === "pipeline" && isInspectorOpen && (
        <Inspector
          selected={selected}
          text={text}
          setText={setText}
          result={result}
          loading={loading}
          error={error}
          analyze={analyze}
          agent={selectedAgent}
          includeAzure={includeAzure}
          setIncludeAzure={setIncludeAzure}
          inputViewMode={inputViewMode}
          setInputViewMode={setInputViewMode}
          pdfLoading={pdfLoading}
          pdfInfo={pdfInfo}
          handlePdfUpload={handlePdfUpload}
          onClearPdf={onClearPdf}
          remediations={remediations}
          remediating={remediating}
          handleRemediate={handleRemediate}
          handleApplyRemediation={handleApplyRemediation}
          onOpenFullAnalysis={() => setView("analysis")}
          onOpenTelemetry={openTelemetry}
          onClose={() => setIsInspectorOpen(false)}
        />
      )}

      {studioMode === "pipeline" && !isInspectorOpen && (
        <button
          type="button"
          className="floating-inspector-open-tab no-print"
          onClick={() => setIsInspectorOpen(true)}
          title="Open Node Inspector (Press [I])"
        >
          <Layers3 size={15} />
          <span>Inspect Node</span>
          <ChevronRight size={13} style={{ transform: "rotate(180deg)" }} />
        </button>
      )}

      <FloatingInputModal
        isOpen={isInputModalOpen}
        onClose={() => setIsInputModalOpen(false)}
        text={text}
        setText={setText}
        loading={loading}
        analyze={analyze}
        pdfLoading={pdfLoading}
        pdfInfo={pdfInfo}
        handlePdfUpload={handlePdfUpload}
        onClearPdf={onClearPdf}
      />

      <DossierHistoryDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectCase={(c) => {
          setText(c.text);
          if (c.result) setResult(c.result);
          setSelected("dossier");
        }}
      />

      <ShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />

      <ModelTelemetryModal
        isOpen={Boolean(telemetryModal)}
        onClose={() => setTelemetryModal(null)}
        agentId={telemetryModal?.agentId || "archaeologist"}
        agent={telemetryModal?.agentId ? AGENTS[telemetryModal.agentId] : null}
        agentData={telemetryModal?.agentId ? result?.agents?.[telemetryModal.agentId] : null}
        initialTab={telemetryModal?.tab || "labels"}
        text={text}
      />
    </div>
  );
}

/* ================= SIDEBAR ================= */

function Sidebar({
  selected,
  setSelected,
  backendStatus,
  view,
  setView,
  result,
  onOpenHistory,
  currentUser,
  onLogout,
  studioMode,
  setStudioMode,
}) {
  const isOnline = backendStatus?.online;
  const isLoading = backendStatus?.loading;
  const groups = [
    {
      title: "PLATFORM",
      items: [
        ["1. Input & Document Ingestion", FileUp, "input_screen"],
        ["2. 5-Model Neural Flow", Workflow, "pipeline_flow"],
        ["3. Full Analysis Dossier", FileText, "analysis"],
        ["Product Landing", Globe, "landing"],
        ["Case Archive", History, "history"],
      ],
    },
    {
      title: "INTELLIGENCE",
      items: [
        ["Agent Network", Network, "synthesizer"],
        ["Evidence Graph", GitBranch, "historian"],
      ],
    },
    {
      title: "SYSTEM",
      items: [
        ["Models", Layers3, "archaeologist"],
        ["Knowledge Base", Database, "historian"],
        ["Configuration", Settings2, "dossier"],
      ],
    },
  ];

  return (
    <aside className="sidebar">
      <div className="brand" onClick={() => setView("landing")} style={{ cursor: "pointer" }} title="Back to Overview">
        <div className="brand-mark">
          <i />
        </div>

        <div>
          <strong>L.I.M.I.N.A.L.</strong>

          <small>
            AI-103 / INTELLIGENCE ENGINE
          </small>
        </div>
      </div>

      <div className="sidebar-scroll">
        {groups.map((group) => (
          <section
            className="sidebar-group"
            key={group.title}
          >
            <label>{group.title}</label>

            {group.items.map(
              ([name, Icon, node]) => {
                const active =
                  (node === "input_screen" && studioMode === "input") ||
                  (node === "pipeline_flow" && studioMode === "pipeline" && view === "studio") ||
                  (node === "analysis" && view === "analysis") ||
                  (studioMode === "pipeline" && selected === node);

                return (
                  <button
                    key={name}
                    className={`sidebar-item ${
                      active ? "active" : ""
                    }`}
                    onClick={() => {
                      if (node === "input_screen") {
                        setStudioMode && setStudioMode("input");
                      } else if (node === "pipeline_flow") {
                        setStudioMode && setStudioMode("pipeline");
                      } else if (name === "Case Archive" || name === "Dossiers") {
                        onOpenHistory && onOpenHistory();
                      } else if (node === "landing") {
                        setView("landing");
                      } else if (node === "analysis") {
                        if (result) {
                          setView("analysis");
                        } else {
                          setSelected("dossier");
                        }
                      } else {
                        setStudioMode && setStudioMode("pipeline");
                        setSelected(node);
                      }
                    }}
                  >
                    <Icon size={14} />

                    <span>{name}</span>

                    {node === "analysis" && result && (
                      <span className="sidebar-ready-badge">Ready</span>
                    )}

                    {active && (
                      <ChevronRight
                        size={12}
                      />
                    )}
                  </button>
                );
              }
            )}
          </section>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="system-card">
          <div className="system-title">
            <i className={isOnline ? "online-dot" : "offline-dot"} />
            {isOnline ? "SYSTEM ONLINE" : isLoading ? "CONNECTING..." : "SYSTEM OFFLINE"}
          </div>

          <div className="system-sub">
            <span className="system-mode-tag">
              Agents {isOnline ? "operational" : "offline"}
            </span>
            <span className="system-sub-desc">
              {isOnline ? "Multi-agent inference ready" : "Start FastAPI on port 8000"}
            </span>
          </div>

          <SystemRow
            label="COMPUTE"
            value={isOnline ? (backendStatus?.device?.toUpperCase() === "CUDA" ? "RTX 3050 / CUDA" : backendStatus?.device?.toUpperCase() || "CUDA") : "OFFLINE"}
          />

          <SystemRow
            label="VECTOR DB"
            value={isOnline ? "FAISS" : "OFFLINE"}
          />

          <SystemRow
            label="AZURE"
            value={isOnline ? (backendStatus?.azure_explainer === "ready" ? "READY" : backendStatus?.azure_explainer || "DISABLED") : "OFFLINE"}
            green={backendStatus?.azure_explainer === "ready"}
          />
        </div>

        {/* User Account Card & Logout */}
        <div className="sidebar-account-card">
          <div className="sidebar-account-header">
            <div className="sidebar-account-avatar">
              {currentUser?.photoURL ? (
                <img src={currentUser.photoURL} alt="Avatar" />
              ) : (
                <User size={13} />
              )}
            </div>
            <div className="sidebar-account-info">
              <strong className="sidebar-account-name">
                {currentUser?.displayName || "Analyst Session"}
              </strong>
              <small className="sidebar-account-email">
                {currentUser?.email || "Local Workstation"}
              </small>
            </div>
          </div>
          <button
            type="button"
            className="sidebar-account-logout-btn"
            onClick={onLogout}
            title="Log out and switch account"
          >
            <LogOut size={12} />
            <span>Switch Account</span>
          </button>
        </div>

        <div className="responsible">
          <ShieldCheck size={13} />
          Responsible AI
        </div>
      </div>
    </aside>
  );
}

function SystemRow({
  label,
  value,
  green = false,
}) {
  return (
    <div className="system-row">
      <span>{label}</span>

      <strong className={green ? "green" : ""}>
        {value}
      </strong>
    </div>
  );
}

/* ================= TOPBAR ================= */

function Topbar({
  resetCanvas,
  loading,
  backendStatus,
  onOpenShortcuts,
  isInspectorOpen,
  setIsInspectorOpen,
  studioMode,
}) {
  const isOnline = backendStatus?.online;
  return (
    <header className="topbar">
      <div className="breadcrumbs">
        <span>WORKSPACES</span>

        <ChevronRight size={11} />

        <span>L.I.M.I.N.A.L.</span>

        <ChevronRight size={11} />

        <strong>{studioMode === "input" ? "STAGE 01: INGESTION" : "5-MODEL NEURAL PIPELINE"}</strong>
      </div>

      <div className="topbar-actions">
        <button
          className="overview-switch-btn"
          onClick={onOpenShortcuts}
          title="Keyboard Shortcuts (?)"
        >
          <Keyboard size={13} />
          Hotkeys
        </button>

        <button
          className={`overview-switch-btn inspector-toggle-btn ${isInspectorOpen ? "active" : ""}`}
          onClick={() => setIsInspectorOpen && setIsInspectorOpen((open) => !open)}
          title="Toggle Node Inspector Sidebar (Press [I])"
        >
          <Layers3 size={13} />
          <span>{isInspectorOpen ? "Hide Inspector" : "Show Inspector"}</span>
        </button>

        <div className="engine-status">
          <i
            className={
              loading
                ? "status-pulse"
                : isOnline
                ? "online-dot"
                : "offline-dot"
            }
          />

          {loading
            ? "INFERENCE RUNNING"
            : isOnline
            ? "LOCAL INFERENCE ENGINE"
            : "BACKEND OFFLINE"}
        </div>

        <button
          className="reset-button"
          onClick={resetCanvas}
        >
          <RotateCcw size={13} />
          Reset
        </button>
      </div>
    </header>
  );
}

/* ================= CANVAS HEADER ================= */

function CanvasHeader() {
  return (
    <div className="canvas-header">
      <h1>Liminal Inference Pipeline</h1>
    </div>
  );
}

/* ================= FLOATING INPUT MODAL ================= */

function FloatingInputModal({
  isOpen,
  onClose,
  text,
  setText,
  loading,
  analyze,
  pdfLoading,
  pdfInfo,
  handlePdfUpload,
  onClearPdf,
}) {
  if (!isOpen) return null;

  return (
    <div className="floating-input-backdrop" onClick={onClose}>
      <div className="floating-input-modal" onClick={(e) => e.stopPropagation()}>
        <div className="floating-input-header">
          <div className="floating-input-title-group">
            <Send size={18} className="text-green" />
            <div>
              <h3>Communication Input & Scenarios</h3>
              <small>Type, paste, or select a message to analyze for hidden subtext</small>
            </div>
          </div>
          <button
            type="button"
            className="floating-input-close-btn"
            onClick={onClose}
            title="Close (Esc)"
          >
            <X size={18} />
          </button>
        </div>

        <div className="floating-input-body">
          {/* Quick Scenario Pills */}
          <div className="floating-input-presets">
            <span className="preset-bar-title">Quick Test Scenarios:</span>
            <div className="preset-chips-wrap">
              {PRESETS.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className="preset-chip-pill"
                  onClick={() => setText(p.text)}
                  title={p.description || p.title}
                >
                  {p.title}
                </button>
              ))}
            </div>
          </div>

          <div className="floating-textarea-container">
            <textarea
              className="floating-input-textarea"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste or type an email, meeting statement, memo, or message here..."
              rows={6}
              autoFocus
            />
            <div className="floating-textarea-footer">
              <span className="char-count">{text.length} characters</span>
              <span className="tip-note">Tip: Hedging terms ("probably", "should") and passive phrases trigger rich forensic signals.</span>
            </div>
          </div>

          {/* Document / PDF Upload Row */}
          <div className="floating-input-upload-row">
            <label className="floating-pdf-btn">
              <Upload size={14} />
              <span>{pdfLoading ? "Extracting text..." : "Upload Executive PDF"}</span>
              <input
                type="file"
                accept=".pdf"
                style={{ display: "none" }}
                onChange={handlePdfUpload}
                disabled={pdfLoading}
              />
            </label>
            {pdfInfo && (
              <div className="pdf-info-chip">
                <span>{pdfInfo.name} ({pdfInfo.pages} pages)</span>
                <button type="button" onClick={onClearPdf} title="Remove PDF">
                  <X size={12} />
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="floating-input-footer">
          <button type="button" className="floating-btn-cancel" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="floating-btn-analyze"
            disabled={loading || !text.trim()}
            onClick={() => {
              onClose();
              analyze();
            }}
          >
            {loading ? (
              <>
                <LoaderCircle size={15} className="spin" />
                <span>Running Pipeline...</span>
              </>
            ) : (
              <>
                <Play size={14} fill="currentColor" />
                <span>Run Forensic Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ================= INPUT NODE ================= */

function InputNode({
  text,
  loading,
  selected,
  onSelect,
  analyze,
  onOpenInputModal,
  onEditInput,
}) {
  return (
    <div
      className={`workflow-node input-node ${
        selected ? "selected" : ""
      } ${loading ? "processing" : ""}`}
      style={{
        left: 35,
        top: 390,
      }}
      onPointerDown={(e) =>
        e.stopPropagation()
      }
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
        if (onEditInput) {
          onEditInput();
        } else if (onOpenInputModal) {
          onOpenInputModal();
        }
      }}
      title="Click to edit message in full ingestion screen"
    >
      <NodeTop
        number="00"
        icon={Send}
        title="INPUT"
        status={
          loading ? "PROCESSING" : "READY"
        }
      />

      <div className="input-card-content">
        <h3>Input Communication</h3>
        <span className="agent-friendly-role">Step 1: Raw payload to analyze</span>

        <div
          className="input-text-preview-box"
          onClick={(e) => {
            e.stopPropagation();
            if (onEditInput) {
              onEditInput();
            } else if (onOpenInputModal) {
              onOpenInputModal();
            }
          }}
          title="Click to open full ingestion screen"
        >
          <p className="preview-quote">
            "{text.length > 95 ? text.slice(0, 95) + "..." : text}"
          </p>
          <div className="preview-meta-row">
            <span>{text.length} chars</span>
            <span className="edit-action-pill">
              ✏️ Click to Edit Input & PDF
            </span>
          </div>
        </div>
      </div>

      <div className="input-footer">
        <button
          type="button"
          className="node-action-btn primary"
          disabled={loading}
          onPointerDown={(e) =>
            e.stopPropagation()
          }
          onClick={(e) => {
            e.stopPropagation();
            analyze();
          }}
        >
          {loading ? (
            <LoaderCircle
              size={13}
              className="spin"
            />
          ) : (
            <Play
              size={12}
              fill="currentColor"
            />
          )}

          {loading ? "Analyzing..." : "Run Analysis"}
        </button>
      </div>
    </div>
  );
}

/* ================= AGENT NODE ================= */

function AgentNode({
  id,
  agent,
  stage,
  result,
  selected,
  onSelect,
  text = "",
  onOpenTelemetry,
  loading = false,
}) {
  const Icon = agent.icon;

  const agentIndex = STAGES.indexOf(id);
  const currentIndex = STAGES.indexOf(stage);
  const isActivelyAnalyzing = loading && (stage === id || (stage === "input" && id === "archaeologist"));
  const complete = Boolean(result) || currentIndex > agentIndex;
  const data = result?.agents?.[id] || {};

  const showOperationAnim = isActivelyAnalyzing;

  const prediction = data.prediction || data.label || null;
  const probability = data.probability ?? data.confidence;

  const findings = Array.isArray(data.findings)
    ? data.findings
    : Array.isArray(data.evidence)
    ? data.evidence
    : Array.isArray(data)
    ? data
    : data.class_probabilities
    ? Object.entries(data.class_probabilities).map(([label, probability]) => ({
        label,
        probability,
      }))
    : [];

  // Parse raw message tokens
  const rawTokens =
    data.tokens && data.tokens.length > 0
      ? data.tokens
      : text
      ? text
          .toLowerCase()
          .replace(/[^\w\s']/g, " ")
          .trim()
          .split(/\s+/)
          .filter(Boolean)
      : [];

  // Dynamic telemetry calculations
  const vocabSize =
    data.vocab_size ||
    (id === "archaeologist"
      ? 326
      : id === "psychologist"
      ? 216
      : id === "logician"
      ? 466
      : id === "historian"
      ? 18
      : 25);

  const totalLabels =
    id === "logician"
      ? 6
      : id === "historian"
      ? 5
      : id === "synthesizer"
      ? 8
      : 7;

  // Active labels count
  const allLabels = Array.isArray(data.all_labels) ? data.all_labels : [];
  const activeLabelsCount =
    allLabels.length > 0
      ? allLabels.filter((l) => l.active || l.probability >= 0.5).length
      : prediction
      ? 1
      : findings.filter((f) => (f.probability ?? f.confidence ?? 1) >= 0.5).length;

  const inVocabCount =
    data.in_vocab_tokens?.length ??
    (complete && rawTokens.length > 0
      ? Math.min(rawTokens.length, vocabSize)
      : rawTokens.length > 0
      ? Math.min(rawTokens.length, Math.floor(rawTokens.length * 0.75))
      : 0);

  // Dynamic chip badge 1 (Architecture)
  const archLabel =
    id === "historian"
      ? "FAISS"
      : id === "synthesizer"
      ? "Fusion Net"
      : "Transformer";

  // Dynamic chip badge 2 (Vocab / Records)
  const vocabChipText =
    id === "historian"
      ? `${complete && findings.length ? findings.length : 18} records`
      : id === "synthesizer"
      ? "25 features"
      : complete
      ? `${inVocabCount} in / ${vocabSize} vocab`
      : `${rawTokens.length || 0} tok • ${vocabSize} vocab`;

  // Dynamic chip badge 3 (Labels)
  const labelsChipText = complete
    ? `${activeLabelsCount}/${totalLabels} active`
    : `${totalLabels} labels`;

  // Friendly plain-English agent role tags
  const friendlyRole =
    id === "archaeologist"
      ? "Structural Omissions & Hedging"
      : id === "psychologist"
      ? "Tone & Hidden Reluctance"
      : id === "logician"
      ? "Premises & Logical Fallacies"
      : id === "historian"
      ? "Pragmatics & Linguistics Grounding"
      : "Multi-Model Fusion & Calibration";

  return (
    <div
      className={`workflow-node agent-node ${agent.color} ${
        selected ? "selected" : ""
      } ${isActivelyAnalyzing ? "analyzing-active processing" : ""} ${
        complete ? "complete" : ""
      }`}
      style={{
        left: agent.x,
        top: agent.y,
      }}
      onPointerDown={(e) =>
        e.stopPropagation()
      }
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
    >
      <div className="node-accent" />

      <NodeTop
        number={agent.number}
        icon={Icon}
        title={agent.name.toUpperCase()}
        status={
          showOperationAnim
            ? "ANALYZING"
            : complete
            ? "COMPLETE"
            : "STANDBY"
        }
      />

      <h3>{agent.subtitle}</h3>
      <span className="agent-friendly-role">{friendlyRole}</span>

      {/* Live "Analysis in Progress" Animation Banner - shown once then disappears */}
      {showOperationAnim && (
        <div className="node-live-analyzing-banner">
          <div className="radar-pulse-dot" />
          <LoaderCircle size={12} className="spin text-cyan" />
          <span className="live-analyzing-text">
            {id === "archaeologist"
              ? "Scanning structural hedges & passive voice..."
              : id === "psychologist"
              ? "Analyzing tone & affect..."
              : id === "logician"
              ? "Validating premises & logic..."
              : id === "historian"
              ? "Retrieving Gricean evidence..."
              : "Synthesizing multi-agent tensor..."}
          </span>
        </div>
      )}

      <p>{agent.description}</p>

      {/* Dynamic, interactive model telemetry chips */}
      <div className="node-chips">
        <button
          type="button"
          className="node-chip-btn"
          onClick={(e) => {
            e.stopPropagation();
            onOpenTelemetry && onOpenTelemetry("architecture");
          }}
          title="Inspect neural architecture, layer topology and CUDA acceleration"
        >
          <span>⚡ {archLabel}</span>
        </button>

        <button
          type="button"
          className="node-chip-btn"
          onClick={(e) => {
            e.stopPropagation();
            onOpenTelemetry && onOpenTelemetry("vocab");
          }}
          title="Inspect extracted tokens, in-vocab matches and model dictionary"
        >
          <span>📖 {vocabChipText}</span>
        </button>

        <button
          type="button"
          className={`node-chip-btn ${activeLabelsCount > 0 && complete ? "active-signal" : ""}`}
          onClick={(e) => {
            e.stopPropagation();
            onOpenTelemetry && onOpenTelemetry("labels");
          }}
          title="Inspect multi-label probability distributions and thresholds"
        >
          {activeLabelsCount > 0 && complete && <i className="node-chip-dot" />}
          <span>🏷️ {labelsChipText}</span>
        </button>
      </div>

      <div
        className="node-result clickable"
        onClick={(e) => {
          e.stopPropagation();
          onOpenTelemetry && onOpenTelemetry("labels");
        }}
        title="Click to inspect signal telemetry and calibrated probabilities"
      >
        <div>
          <small>
            PRIMARY SIGNAL
          </small>

          <strong>
            {prediction ? (
              <span className="signal-live-badge has-signal">
                <i className="node-chip-dot" />
                {formatLabel(prediction)}
                {probability !== undefined && (
                  <span className="signal-pct"> ({(probability <= 1 ? probability * 100 : probability).toFixed(0)}%)</span>
                )}
              </span>
            ) : findings.length ? (
              id === "historian" ? (
                `${findings.length} records retrieved`
              ) : (
                <span className="signal-live-badge has-signal">
                  <i className="node-chip-dot" />
                  {formatLabel(findings[0].label || `${findings.length} findings`)}
                  {findings[0].probability !== undefined && (
                    <span className="signal-pct"> ({(findings[0].probability <= 1 ? findings[0].probability * 100 : findings[0].probability).toFixed(0)}%)</span>
                  )}
                </span>
              )
            ) : complete ? (
              "No anomalous signal (Sub-threshold)"
            ) : (
              "Awaiting analysis"
            )}
          </strong>
        </div>

        <ArrowUpRight size={15} />
      </div>

      {showOperationAnim && (
        <div className="processing-line">
          <i />
        </div>
      )}
    </div>
  );
}

function NodeTop({
  number,
  icon: Icon,
  title,
  status,
}) {
  return (
    <div className="node-top">
      <div className="node-icon">
        <Icon size={18} />
      </div>

      <span className="node-number">
        {number}
      </span>

      <strong>{title}</strong>

      <span className="node-status">
        <i
          className={
            status === "ANALYZING"
              ? "status-pulse"
              : status === "COMPLETE" ||
                status === "READY"
              ? "online-dot"
              : "status-off"
          }
        />

        {status}
      </span>
    </div>
  );
}

/* ================= EDGES ================= */

function WorkflowEdges({
  stageIndex,
  loading,
}) {
  const edges = [
    {
      id: "input-arch",
      d: "M305 500 H365",
      from: 0,
      to: 1,
    },

    {
      id: "arch-psych",
      d: "M665 500 H680 V170 H705",
      from: 1,
      to: 2,
    },

    {
      id: "arch-logic",
      d: "M665 500 H705",
      from: 1,
      to: 3,
    },

    {
      id: "arch-history",
      d: "M665 500 H680 V840 H705",
      from: 1,
      to: 4,
    },

    {
      id: "psych-synth",
      d: "M1005 170 H1025 V455 H1050",
      from: 2,
      to: 5,
    },

    {
      id: "logic-synth",
      d: "M1005 500 H1050",
      from: 3,
      to: 5,
    },

    {
      id: "history-synth",
      d: "M1005 840 H1025 V545 H1050",
      from: 4,
      to: 5,
    },

    {
      id: "synth-dossier",
      d: "M1350 500 H1380",
      from: 5,
      to: 6,
    },
  ];

  return (
    <svg
      className="workflow-edges"
      viewBox="0 0 1700 1200"
      preserveAspectRatio="none"
    >
      <defs>
        <filter
          id="threadGlow"
          x="-200%"
          y="-200%"
          width="400%"
          height="400%"
        >
          <feGaussianBlur
            stdDeviation="3"
            result="blur"
          />

          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {edges.map((edge) => {
        const completed =
          stageIndex >= edge.to;

        const active =
          loading &&
          stageIndex >= edge.from &&
          stageIndex <= edge.to;

        return (
          <g key={edge.id}>
            <path
              d={edge.d}
              className="edge-shadow"
            />

            <path
              d={edge.d}
              className={`edge ${
                completed ? "completed" : ""
              } ${
                active ? "active" : ""
              }`}
            />

            {(completed || active) && (
              <>
                <path
                  d={edge.d}
                  className="edge-flow"
                />

                <circle
                  r="4.5"
                  className="edge-packet"
                  filter="url(#threadGlow)"
                >
                  <animateMotion
                    dur="1.4s"
                    repeatCount="indefinite"
                    path={edge.d}
                  />
                </circle>
              </>
            )}
          </g>
        );
      })}
    </svg>
  );
}

/* ================= EVIDENCE ================= */

function Evidence({
  visible,
  result,
}) {
  if (!visible) return null;

  const evidence =
    result?.dossier?.evidence ||
    result?.evidence ||
    result?.historian?.evidence ||
    result?.agents?.historian?.evidence ||
    (Array.isArray(result?.agents?.historian)
      ? result.agents.historian
      : []);

  const fallback = [
    {
      title:
        "Conversational implicature",
      source:
        "Stanford Encyclopedia of Philosophy",
      score: 0.82,
    },
    {
      title: "Quantity maxim",
      source:
        "Stanford Encyclopedia of Philosophy",
      score: 0.78,
    },
    {
      title:
        "Logical consequence",
      source:
        "Stanford Encyclopedia of Philosophy",
      score: 0.74,
    },
  ];

  const records =
    Array.isArray(evidence) &&
    evidence.length
      ? evidence.slice(0, 3)
      : fallback;

  return (
    <div
      className="evidence"
      style={{
        left: 705,
        top: 1050,
      }}
    >
      <div className="evidence-heading">
        <span>
          <Database size={14} />
          RETRIEVED EVIDENCE
        </span>

        <strong>
          {records.length} RECORDS
        </strong>
      </div>

      <div className="evidence-row">
        {records.map((item, index) => {
          const title =
            item.title ||
            item.topic ||
            item.name ||
            `Evidence ${index + 1}`;

          const source =
            item.source ||
            item.origin ||
            "Knowledge Base";

          const score = Number(
            item.similarity ??
              item.score ??
              0.7
          );

          return (
            <div
              className="evidence-card"
              key={`${title}-${index}`}
            >
              <em>
                0{index + 1}
              </em>

              <div>
                <strong>
                  {title}
                </strong>

                <small>
                  {source}
                </small>
              </div>

              <b>
                {(score * 100).toFixed(0)}%
              </b>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ================= DOSSIER ================= */

function DossierNode({
  result,
  stage,
  selected,
  onSelect,
  onOpenFullAnalysis,
}) {
  const visible =
    stage === "dossier" ||
    Boolean(result);

  const metrics = result ? computeForensicMetrics(result) : null;

  const prediction =
    metrics?.primaryPattern ||
    result?.dossier?.primary_pattern ||
    result?.dossier?.prediction ||
    result?.agents?.synthesizer?.prediction ||
    "Awaiting Synthesis";

  const confidence =
    metrics ? metrics.confidence : getConfidence(result);

  return (
    <div
      className={`workflow-node dossier-node ${
        selected ? "selected" : ""
      } ${
        visible ? "complete" : ""
      }`}
      style={{
        left: 1380,
        top: 390,
      }}
      onPointerDown={(e) =>
        e.stopPropagation()
      }
      onClick={(e) => {
        e.stopPropagation();
        onSelect();
      }}
    >
      <div className="dossier-glow" />

      <NodeTop
        number="06"
        icon={ClipboardList}
        title="DOSSIER"
        status={
          visible
            ? "GENERATED"
            : "WAITING"
        }
      />

      <h3>
        Subtext Dossier
      </h3>

      <div className="dossier-pattern">
        {formatLabel(prediction)}
      </div>

      <div className="dossier-confidence">
        <div>
          <small>
            MODEL CONFIDENCE
          </small>

          <strong>
            {confidence.toFixed(1)}%
          </strong>
        </div>

        <ConfidenceRing
          value={confidence}
        />
      </div>

      <div className="dossier-footer">
        <span>
          OBSERVATION ≠ MIND READING
        </span>

        <ShieldCheck size={14} />
      </div>

      {visible && (
        <button
          type="button"
          className="dossier-full-page-btn"
          onClick={(e) => {
            e.stopPropagation();
            onOpenFullAnalysis && onOpenFullAnalysis();
          }}
          title="Open Dedicated Full-Screen Forensic Analysis Dossier"
        >
          <ExternalLink size={13} />
          <span>Open Full Analysis Page ↗</span>
        </button>
      )}
    </div>
  );
}

/* ================= CONTROLS ================= */

function CanvasControls({
  zoom,
  setZoom,
  resetCanvas,
}) {
  return (
    <div className="canvas-controls">
      <button
        onPointerDown={(e) =>
          e.stopPropagation()
        }
        onClick={(e) => {
          e.stopPropagation();

          setZoom((z) =>
            Math.max(
              0.62,
              z - 0.05
            )
          );
        }}
      >
        <ZoomOut size={15} />
      </button>

      <span>
        {Math.round(zoom * 100)}%
      </span>

      <button
        onPointerDown={(e) =>
          e.stopPropagation()
        }
        onClick={(e) => {
          e.stopPropagation();

          setZoom((z) =>
            Math.min(
              0.9,
              z + 0.05
            )
          );
        }}
      >
        <ZoomIn size={15} />
      </button>

      <button
        className="control-reset"
        onPointerDown={(e) =>
          e.stopPropagation()
        }
        onClick={(e) => {
          e.stopPropagation();
          resetCanvas();
        }}
      >
        Reset
      </button>
    </div>
  );
}

/* ================= INSPECTOR ================= */

function Inspector({
  selected,
  text,
  setText,
  result,
  loading,
  error,
  analyze,
  agent,
  includeAzure,
  setIncludeAzure,
  inputViewMode,
  setInputViewMode,
  pdfLoading,
  pdfInfo,
  handlePdfUpload,
  onClearPdf,
  remediations,
  remediating,
  handleRemediate,
  handleApplyRemediation,
  onOpenFullAnalysis,
  onOpenTelemetry,
  onClose,
}) {
  return (
    <aside className="inspector">
      <header className="inspector-header">
        <div>
          <small>
            NODE INSPECTOR
          </small>

          <h2>
            {selected === "input"
              ? "Communication Input"
              : selected === "dossier"
              ? "Subtext Dossier"
              : agent?.name ||
                "Agent"}
          </h2>
        </div>

        <div className="inspector-header-actions">
          <button
            type="button"
            className="inspector-close-btn"
            onClick={onClose}
            title="Close Inspector Sidebar (Press [I])"
          >
            <X size={16} />
          </button>
        </div>
      </header>

      {selected === "input" && (
        <InputInspector
          text={text}
          setText={setText}
          result={result}
          loading={loading}
          error={error}
          analyze={analyze}
          includeAzure={includeAzure}
          setIncludeAzure={setIncludeAzure}
          inputViewMode={inputViewMode}
          setInputViewMode={setInputViewMode}
          pdfLoading={pdfLoading}
          pdfInfo={pdfInfo}
          handlePdfUpload={handlePdfUpload}
          onClearPdf={onClearPdf}
        />
      )}

      {agent && (
        <AgentInspector
          agent={agent}
          result={result}
          loading={loading}
          text={text}
          onOpenTelemetry={onOpenTelemetry}
        />
      )}

      {selected === "dossier" && (
        <DossierInspector
          result={result}
          loading={loading}
          text={text}
          remediations={remediations}
          remediating={remediating}
          handleRemediate={handleRemediate}
          handleApplyRemediation={handleApplyRemediation}
          onOpenFullAnalysis={onOpenFullAnalysis}
        />
      )}
    </aside>
  );
}

/* ================= INPUT INSPECTOR ================= */

function InputInspector({
  text,
  setText,
  result,
  loading,
  error,
  analyze,
  includeAzure,
  setIncludeAzure,
  inputViewMode = "edit",
  setInputViewMode,
  pdfLoading,
  pdfInfo,
  handlePdfUpload,
  onClearPdf,
}) {
  const fileInputRef = useRef(null);

  return (
    <div className="inspector-scroll">
      <InspectorHero
        icon={Send}
        title="Communication Input"
        subtitle="Primary analysis payload"
      />

      <section className="inspector-section">
        <SectionLabel>
          MESSAGE
        </SectionLabel>

        {/* PDF Document Upload Zone */}
        <div className="pdf-upload-container">
          <input
            type="file"
            accept=".pdf"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={(e) => {
              if (e.target.files?.[0]) {
                handlePdfUpload(e.target.files[0]);
              }
            }}
          />
          {pdfInfo ? (
            <div className="pdf-file-info">
              <span className="pdf-file-title">
                <FileUp size={13} />
                {pdfInfo.filename} ({pdfInfo.pages}p / {pdfInfo.characters}c)
              </span>
              <button
                type="button"
                className="pdf-clear-btn"
                onClick={onClearPdf}
                title="Clear uploaded PDF"
              >
                <X size={12} />
              </button>
            </div>
          ) : (
            <div
              className="pdf-dropzone"
              onClick={() => fileInputRef.current?.click()}
              title="Upload executive memo, transcript or document in PDF format"
            >
              {pdfLoading ? <LoaderCircle size={13} className="spin" /> : <Upload size={13} />}
              <span>{pdfLoading ? "Extracting PDF text..." : "Upload Memo / PDF Document"}</span>
            </div>
          )}
        </div>

        <div className="preset-pills-row">
          <small className="preset-label">SCENARIO PRESETS:</small>
          <div className="preset-pills">
            {PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                className={`preset-pill ${text === p.text ? "active" : ""}`}
                onClick={() => setText(p.text)}
                title={p.description}
              >
                {p.title}
              </button>
            ))}
          </div>
        </div>

        {/* View Switch: Plain Editor vs Forensic Signals */}
        <div className="input-view-switch">
          <button
            type="button"
            className={`input-view-tab ${inputViewMode === "edit" ? "active" : ""}`}
            onClick={() => setInputViewMode("edit")}
          >
            <FileText size={11} />
            Message Editor
          </button>
          <button
            type="button"
            className={`input-view-tab ${inputViewMode === "forensics" ? "active" : ""}`}
            onClick={() => setInputViewMode("forensics")}
          >
            <ScanSearch size={11} />
            Forensic Signals
          </button>
        </div>

        {inputViewMode === "forensics" ? (
          <ForensicHighlighter text={text} result={result} />
        ) : (
          <textarea
            className="inspector-textarea"
            value={text}
            onChange={(e) =>
              setText(e.target.value)
            }
          />
        )}

        <div className="textarea-meta">
          <span>
            {text.length} characters
          </span>

          <span>MAX 5,000</span>
        </div>

        <div className="inspector-toggle-row">
          <label className="toggle-label" htmlFor="azure-ai-toggle">
            <span className="toggle-title">Azure GPT-6 Synthesis</span>
            <span className="toggle-desc">
              {includeAzure ? "Astra deep reasoning enabled" : "Fast local inference (~0.3s)"}
            </span>
          </label>
          <input
            id="azure-ai-toggle"
            type="checkbox"
            className="toggle-checkbox"
            checked={includeAzure}
            onChange={(e) => setIncludeAzure && setIncludeAzure(e.target.checked)}
          />
        </div>
      </section>

      {error && (
        <div className="error-box">
          {error}
        </div>
      )}

      <button
        className="analyze-button"
        disabled={loading}
        onClick={analyze}
      >
        {loading ? (
          <>
            <LoaderCircle
              size={16}
              className="spin"
            />

            RUNNING PIPELINE
          </>
        ) : (
          <>
            <Sparkles size={16} />

            RUN L.I.M.I.N.A.L.
          </>
        )}
      </button>

      <section className="inspector-section">
        <SectionLabel>
          PIPELINE CONTRACT
        </SectionLabel>

        <div className="contract-list">
          {[
            "Linguistic forensics",
            "Affect analysis",
            "Reasoning analysis",
            "Evidence retrieval",
            "Subtext synthesis",
          ].map((item, index) => (
            <div
              className="contract-row"
              key={item}
            >
              <span>
                0{index + 1}
              </span>

              <strong>
                {item}
              </strong>

              <Check size={14} />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ================= AGENT INSPECTOR ================= */

function AgentInspector({
  agent,
  result,
  loading,
  onOpenTelemetry,
}) {
  const Icon = agent.icon;
  const agentKey = agent.name.toLowerCase();

  const data =
    result?.agents?.[agentKey] || {};

  const prediction =
    data.prediction ||
    data.label ||
    null;

  let findings = [];
  if (Array.isArray(data.findings)) {
    findings = data.findings;
  } else if (Array.isArray(data.evidence)) {
    findings = data.evidence;
  } else if (Array.isArray(data)) {
    findings = data;
  } else if (data.class_probabilities) {
    findings = Object.entries(data.class_probabilities)
      .map(([label, probability]) => ({
        label,
        probability,
      }))
      .sort((a, b) => b.probability - a.probability);
  }

  const primarySignal =
    prediction
      ? formatLabel(prediction)
      : findings.length
      ? agentKey === "historian" || findings[0]?.title
        ? `${findings.length} evidence records retrieved`
        : formatLabel(findings[0]?.label || `${findings.length} findings`)
      : result
      ? "No significant signal detected"
      : "Awaiting backend result";

  return (
    <div className="inspector-scroll">
      <InspectorHero
        icon={Icon}
        title={agent.name}
        subtitle={agent.subtitle}
        color={agent.color}
      />

      <div className="model-status">
        <div>
          <small>
            MODEL STATUS
          </small>

          <strong>
            {loading
              ? "INFERENCE ACTIVE"
              : "READY"}
          </strong>
        </div>

        <span>
          <i className="online-dot" />
          CUDA
        </span>
      </div>

      <section className="inspector-section">
        <SectionLabel>
          AGENT OUTPUT
        </SectionLabel>

        <div className="output-card">
          <small>
            PRIMARY SIGNAL
          </small>

          <strong>
            {primarySignal}
          </strong>

          <p>
            {agent.description}
          </p>
        </div>
      </section>

      <section className="inspector-section">
        <SectionLabel>
          SIGNAL FINDINGS
        </SectionLabel>

        <div className="finding-list">
          {findings.length ? (
            findings.map(
              (finding, index) => {
                const label =
                  typeof finding ===
                  "string"
                    ? finding
                    : finding.title ||
                      finding.label ||
                      finding.name ||
                      finding.topic ||
                      "Signal";

                const value =
                  typeof finding ===
                  "string"
                    ? 1
                    : Number(
                        finding.probability ??
                          finding.confidence ??
                          finding.score ??
                          finding.similarity ??
                          0
                      );

                return (
                  <Finding
                    key={`${label}-${index}`}
                    label={label}
                    value={value}
                  />
                );
              }
            )
          ) : (
            <div className="empty-state">
              {loading
                ? "Model is processing..."
                : "Run the pipeline to populate findings."}
            </div>
          )}
        </div>
      </section>

      <section className="inspector-section">
        <SectionLabel>
          MODEL PROFILE & TELEMETRY
        </SectionLabel>

        <div className="profile-grid">
          <button
            type="button"
            className="profile-card-btn"
            onClick={() => onOpenTelemetry && onOpenTelemetry(agentKey, "architecture")}
            title="Inspect Neural Architecture & CUDA Specs"
          >
            <small>MODEL TOPOLOGY</small>
            <strong>⚡ {agentKey === "historian" ? "FAISS Index" : agentKey === "synthesizer" ? "Fusion Net" : "Transformer"}</strong>
          </button>

          <button
            type="button"
            className="profile-card-btn"
            onClick={() => onOpenTelemetry && onOpenTelemetry(agentKey, "vocab")}
            title="Inspect Vocabulary & Tokens"
          >
            <small>VOCABULARY</small>
            <strong>📖 {data.vocab_size || (agentKey === "archaeologist" ? 326 : agentKey === "psychologist" ? 216 : agentKey === "logician" ? 466 : 18)} Tokens</strong>
          </button>

          <button
            type="button"
            className="profile-card-btn"
            onClick={() => onOpenTelemetry && onOpenTelemetry(agentKey, "labels")}
            title="Inspect Active Label Space & Probabilities"
          >
            <small>LABEL SPACE</small>
            <strong>🏷️ {data.all_labels ? `${data.all_labels.filter(l => l.active).length} / ${data.all_labels.length} Active` : agent.meta[2] || "Multi-label"}</strong>
          </button>

          <button
            type="button"
            className="profile-card-btn"
            onClick={() => onOpenTelemetry && onOpenTelemetry(agentKey, "labels")}
            title="Launch Full Model Telemetry Inspector"
          >
            <small>INTERACTIVE TELEMETRY</small>
            <strong style={{ color: "#58f085" }}>Inspect Full ↗</strong>
          </button>
        </div>
      </section>
    </div>
  );
}

/* ================= DOSSIER INSPECTOR ================= */

function DossierInspector({
  result,
  remediations,
  remediating,
  handleRemediate,
  handleApplyRemediation,
  onOpenFullAnalysis,
}) {
  const [copied, setCopied] = useState(false);
  const dossier =
    result?.dossier || {};

  const surface =
    dossier.surface_statement ||
    result?.surface_statement ||
    SAMPLE_TEXT;

  const metrics = computeForensicMetrics(result);

  const prediction = metrics.primaryPattern;
  const confidence = metrics.confidence;
  const subtext =
    dossier.possible_subtext ||
    metrics.severityConfig.summary;

  const missing = metrics.missingItems;

  const explanation =
    dossier.azure_explanation ||
    dossier.explanation ||
    result?.azure_explanation ||
    result?.explanation ||
    "";

  const handleCopyMarkdown = () => {
    const markdown = `# L.I.M.I.N.A.L. Subtext Forensics Briefing
**Timestamp**: ${new Date().toISOString()}
**Primary Classification**: ${formatLabel(prediction)}
**Confidence Score**: ${confidence.toFixed(1)}%

## Surface Statement
> "${surface}"

## Strategically Missing Information
${normalizeArray(missing).map((m) => `- ${formatLabel(m)}`).join("\n")}

## Inferred Subtext
${subtext}

## Azure AI Explanation (GPT-6 Astra)
${explanation || "Pipeline completed via fast local rule & multi-agent neural inference."}

---
*Generated by L.I.M.I.N.A.L. Multi-Agent Linguistic Intelligence System*`;

    navigator.clipboard.writeText(markdown).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2200);
    });
  };

  const handleDownloadJSON = () => {
    const exportData = result || {
      surface_statement: surface,
      prediction,
      confidence,
      possible_subtext: subtext,
      strategically_missing: missing,
      explanation,
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `liminal_dossier_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="inspector-scroll">
      <InspectorHero
        icon={ClipboardList}
        title="Subtext Dossier"
        subtitle="Grounded interpretation"
      />

      <button
        type="button"
        className="dossier-open-full-page-btn"
        onClick={onOpenFullAnalysis}
        title="Open Comprehensive Full-Screen Forensic Analysis Dossier"
      >
        <ExternalLink size={14} />
        <span>OPEN FULL ANALYSIS PAGE ↗</span>
      </button>

      <div className="dossier-actions-row">
        <button
          className={`dossier-action-btn ${copied ? "copied" : ""}`}
          onClick={handleCopyMarkdown}
          title="Copy formatted Markdown briefing to clipboard"
        >
          {copied ? <Check size={13} /> : <Copy size={13} />}
          {copied ? "COPIED BRIEFING" : "COPY BRIEFING"}
        </button>
        <button
          className="dossier-action-btn"
          onClick={handleDownloadJSON}
          title="Download forensic JSON payload"
        >
          <Download size={13} />
          EXPORT JSON
        </button>
      </div>

      {/* Multi-Dimensional Radar Chart */}
      <ForensicRadarChart result={result} />

      <section className="primary-card">
        <SectionLabel>
          PRIMARY PATTERN
        </SectionLabel>

        <h3>
          {formatLabel(prediction)}
        </h3>

        <p>{subtext}</p>
      </section>

      {/* Subtext Remediation Engine */}
      <section className="remediation-section">
        <div className="remediation-header">
          <span className="remediation-tag">
            <Sparkles size={13} />
            SUBTEXT REMEDIATION ENGINE
          </span>
        </div>

        {!remediations ? (
          <button
            type="button"
            className="remediation-trigger-btn"
            onClick={handleRemediate}
            disabled={remediating}
          >
            {remediating ? (
              <>
                <LoaderCircle size={14} className="spin" />
                GENERATING TRANSPARENT REWRITES...
              </>
            ) : (
              <>
                <Sparkles size={14} />
                DRAFT TRANSPARENT REWRITES
              </>
            )}
          </button>
        ) : (
          <div className="remediation-cards-grid">
            <div className="remediation-card">
              <div className="remediation-card-type">
                <span>DIRECT & ASSERTIVE</span>
                <button
                  type="button"
                  className="remediation-apply-btn"
                  onClick={() => handleApplyRemediation(remediations.direct)}
                >
                  Apply to Studio →
                </button>
              </div>
              <div className="remediation-text">"{remediations.direct}"</div>
            </div>

            <div className="remediation-card diplomatic">
              <div className="remediation-card-type diplomatic">
                <span>DIPLOMATIC & CONSTRUCTIVE</span>
                <button
                  type="button"
                  className="remediation-apply-btn"
                  onClick={() => handleApplyRemediation(remediations.diplomatic)}
                >
                  Apply to Studio →
                </button>
              </div>
              <div className="remediation-text">"{remediations.diplomatic}"</div>
            </div>

            {remediations.rationale && (
              <div className="remediation-rationale">
                {remediations.rationale} • {remediations.engine}
              </div>
            )}
          </div>
        )}
      </section>

      <section className="confidence-card">
        <div>
          <SectionLabel>
            MODEL CONFIDENCE
          </SectionLabel>

          <strong>
            {confidence.toFixed(1)}
            <small>%</small>
          </strong>
        </div>

        <ConfidenceRing
          value={confidence}
        />
      </section>

      <section className="inspector-section">
        <SectionLabel>
          SURFACE STATEMENT
        </SectionLabel>

        <div className="surface-box">
          {surface}
        </div>
      </section>

      <section className="inspector-section">
        <SectionLabel>
          STRATEGICALLY MISSING
        </SectionLabel>

        <ul className="missing-list">
          {normalizeArray(missing).map(
            (item, index) => (
              <li
                key={`${item}-${index}`}
              >
                <i />
                {formatLabel(item)}
              </li>
            )
          )}
        </ul>
      </section>

      <section className="azure-card">
        <div className="azure-title">
          <Sparkles size={15} />
          AZURE AI EXPLANATION (GPT-6 ASTRA)
        </div>

        <p className="azure-explanation-text">
          {explanation ||
            "The explanation layer provides a grounded interpretation after the model pipeline completes."}
        </p>

        <small>
          RESPONSIBLE INTERPRETATION
        </small>

        <p>
          Findings describe observable
          communication signals and possible
          subtext. They do not establish
          private thoughts, emotions,
          intentions, or motives as facts.
        </p>
      </section>

      <section className="inspector-section">
        <SectionLabel>
          PIPELINE METRICS
        </SectionLabel>

        <div className="metrics-grid">
          <Metric
            label="AGENTS"
            value="05"
          />

          <Metric
            label="FEATURES"
            value="25"
          />

          <Metric
            label="VECTOR DB"
            value="FAISS"
          />

          <Metric
            label="COMPUTE"
            value="CUDA"
          />
        </div>
      </section>
    </div>
  );
}

/* ================= INSPECTOR HELPERS ================= */

function InspectorHero({
  icon: Icon,
  title,
  subtitle,
  color = "green",
}) {
  return (
    <div
      className={`inspector-hero ${color}`}
    >
      <div>
        <Icon size={22} />
      </div>

      <section>
        <h3>{title}</h3>

        <span>{subtitle}</span>
      </section>
    </div>
  );
}

function SectionLabel({
  children,
}) {
  return (
    <div className="section-label">
      {children}
    </div>
  );
}

function Finding({
  label,
  value,
}) {
  const percentage = Math.max(
    0,
    Math.min(100, value * 100)
  );

  return (
    <div className="finding">
      <div>
        <span>
          {formatLabel(label)}
        </span>

        <strong>
          {percentage.toFixed(1)}%
        </strong>
      </div>

      <i>
        <em
          style={{
            width: `${percentage}%`,
          }}
        />
      </i>
    </div>
  );
}

function Metric({
  label,
  value,
}) {
  return (
    <div className="metric">
      <small>{label}</small>

      <strong>{value}</strong>
    </div>
  );
}

function ConfidenceRing({
  value,
}) {
  const radius = 40;

  const circumference =
    2 * Math.PI * radius;

  const offset =
    circumference -
    (value / 100) * circumference;

  return (
    <div className="confidence-ring">
      <svg viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r={radius}
          className="ring-bg"
        />

        <circle
          cx="50"
          cy="50"
          r={radius}
          className="ring-progress"
          strokeDasharray={
            circumference
          }
          strokeDashoffset={
            offset
          }
        />
      </svg>

      <span>
        {Math.round(value)}
      </span>
    </div>
  );
}

/* ================= BOTTOM BAR ================= */

function BottomBar({
  loading,
  stage,
  result,
  elapsed,
}) {
  return (
    <footer className="bottom-bar">
      <div>
        <span>
          <i
            className={
              loading
                ? "status-pulse"
                : "online-dot"
            }
          />
        </span>

        <strong>
          {loading
            ? `PROCESSING ${stage.toUpperCase()}`
            : result
            ? "PIPELINE COMPLETE"
            : "PIPELINE READY"}
        </strong>

        <i className="separator" />

        <span>5 AGENTS</span>
        <span>CUDA</span>
        <span>FAISS</span>
        <span>AZURE AI</span>
      </div>

      <div>
        <span>
          {elapsed.toFixed(1)}s
        </span>

        <strong>
          {loading
            ? "RUNNING"
            : result
            ? "ANALYSIS COMPLETE"
            : "READY"}
        </strong>
      </div>
    </footer>
  );
}

/* ================= UTILITIES ================= */

function getConfidence(result) {
  if (!result) return 97.1;

  const value =
    result?.dossier?.confidence ??
    result?.confidence ??
    result?.agents?.synthesizer
      ?.confidence ??
    result?.agents?.synthesizer
      ?.model_confidence;

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return 97.1;
  }

  return number <= 1
    ? number * 100
    : number;
}

function normalizeArray(value) {
  if (Array.isArray(value)) {
    return value;
  }

  if (typeof value === "string") {
    return [value];
  }

  return [];
}

function formatLabel(value) {
  if (!value) return "Unknown";

  return String(value)
    .replace(/_/g, " ")
    .replace(/-/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}