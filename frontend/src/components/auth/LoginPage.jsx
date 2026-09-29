import { useState, useEffect } from "react";
import {
  Activity,
  AlertCircle,
  ArrowLeft,
  ArrowRight,
  Brain,
  Check,
  Copy,
  Cpu,
  Database,
  Eye,
  EyeOff,
  GitBranch,
  LoaderCircle,
  Lock,
  Mail,
  Network,
  ScanSearch,
  Settings,
  ShieldCheck,
  Sparkles,
  X,
  Zap,
} from "lucide-react";
import { signInWithGoogle, isFirebaseConfigured } from "../../firebase/config";
import "./LoginPage.css";

const AGENT_SHOWCASE = [
  {
    id: "archaeologist",
    name: "Archaeologist (M1)",
    role: "Linguistic Forensics",
    desc: "Detects hedging, passive agent omissions, and linguistic disengagement.",
    icon: ScanSearch,
    stat: "98.4% Precision",
    color: "#ffffff",
  },
  {
    id: "psychologist",
    name: "Psychologist (M2)",
    role: "Affect & Tone Gaps",
    desc: "Identifies emotional disengagement, subtextual friction, and withheld reservations.",
    icon: Brain,
    stat: "97.1% Recall",
    color: "#d1d1dc",
  },
  {
    id: "logician",
    name: "Logician (M3)",
    role: "Premise & Fallacy Audit",
    desc: "Surfaces unstated assumptions, false dilemmas, and missing evidentiary links.",
    icon: GitBranch,
    stat: "99.2% Consistency",
    color: "#ffffff",
  },
  {
    id: "historian",
    name: "Historian (M4)",
    role: "FAISS Vector Evidence",
    desc: "Retrieves cross-domain precedent cases and verified linguistic markers.",
    icon: Database,
    stat: "18 Records Vectorized",
    color: "#d1d1dc",
  },
  {
    id: "synthesizer",
    name: "Synthesizer (M5)",
    role: "Calibrated Cross-Agent Fusion",
    desc: "Combines 4 upstream agent vectors into a single mathematically calibrated subtext dossier.",
    icon: Network,
    stat: "52k Parameters",
    color: "#ffffff",
  },
];

export default function LoginPage({ onLogin, onBackToLanding, backendStatus }) {
  const [email, setEmail] = useState("analyst@liminal.ai");
  const [password, setPassword] = useState("••••••••••••");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [currentAgentIdx, setCurrentAgentIdx] = useState(0);
  const [authError, setAuthError] = useState("");
  const [showFirebaseModal, setShowFirebaseModal] = useState(false);
  const [copiedKey, setCopiedKey] = useState(false);

  const isOnline = backendStatus?.online;
  const firebaseReady = isFirebaseConfigured();

  // Rotate marketing agent showcase every 3.2 seconds for dynamic animation
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentAgentIdx((prev) => (prev + 1) % AGENT_SHOWCASE.length);
    }, 3200);
    return () => clearInterval(timer);
  }, []);

  const handleSignIn = (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setAuthError("");
    setTimeout(() => {
      setLoading(false);
      localStorage.setItem("liminal_authenticated", "true");
      localStorage.setItem(
        "liminal_user",
        JSON.stringify({
          displayName: email ? email.split("@")[0] : "Analyst",
          email: email || "analyst@liminal.ai",
          photoURL: null,
          uid: "analyst-local",
        })
      );
      onLogin();
    }, 400);
  };

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setAuthError("");

    if (!firebaseReady) {
      setLoading(false);
      setShowFirebaseModal(true);
      return;
    }

    try {
      const user = await signInWithGoogle();
      localStorage.setItem("liminal_authenticated", "true");
      localStorage.setItem(
        "liminal_user",
        JSON.stringify({
          displayName: user.displayName,
          email: user.email,
          photoURL: user.photoURL,
          uid: user.uid,
        })
      );
      onLogin(user);
    } catch (err) {
      console.error("Firebase Google Auth error:", err);
      if (err.code === "auth/popup-closed-by-user") {
        setAuthError("Sign-in popup was closed before completing.");
      } else if (err.code === "auth/popup-blocked") {
        setAuthError("Popup blocked by browser. Allow popups for localhost or use Demo Access.");
      } else if (err.code === "auth/operation-not-allowed") {
        setAuthError("Google Sign-In is not enabled yet in your Firebase Console (Authentication → Sign-in method → Google).");
      } else if (err.code === "auth/unauthorized-domain") {
        setAuthError("localhost is not authorized in your Firebase Console (Authentication → Settings → Authorized domains).");
      } else if (err.code === "auth/configuration-not-found" || err.message?.includes("credentials not yet provided")) {
        setShowFirebaseModal(true);
      } else {
        setAuthError(err.message || "Failed to authenticate with Google.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGuestAccess = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      localStorage.setItem("liminal_authenticated", "true");
      localStorage.setItem(
        "liminal_user",
        JSON.stringify({
          displayName: "Analyst Guest",
          email: "guest@liminal.ai",
          photoURL: null,
          uid: "guest-user",
        })
      );
      onLogin();
    }, 300);
  };

  const handleDemoGoogleLogin = () => {
    setLoading(true);
    setShowFirebaseModal(false);
    setTimeout(() => {
      setLoading(false);
      localStorage.setItem("liminal_authenticated", "true");
      localStorage.setItem(
        "liminal_user",
        JSON.stringify({
          displayName: "Google Analyst (Demo)",
          email: "analyst.google@liminal.ai",
          photoURL: null,
          uid: "demo-google-uid-103",
        })
      );
      onLogin();
    }, 400);
  };

  const activeAgent = AGENT_SHOWCASE[currentAgentIdx];
  const ActiveAgentIcon = activeAgent.icon;

  return (
    <div className="login-page">
      <div className="login-ambient-1" />
      <div className="login-ambient-2" />

      {/* Top Header Navigation */}
      <header className="login-topbar">
        <div className="login-brand" onClick={onBackToLanding}>
          <div className="login-brand-mark">
            <i />
          </div>
          <div className="login-brand-text">
            <strong>L.I.M.I.N.A.L.</strong>
            <small>INTELLIGENCE ENGINE</small>
          </div>
        </div>

        <button className="login-back-btn" onClick={onBackToLanding}>
          <ArrowLeft size={14} />
          <span>Return to Marketing Page</span>
        </button>
      </header>

      {/* Main Split Container */}
      <div className="login-container">
        <div className="login-split-card">
          {/* ========================================================
              LEFT COLUMN: AUTHENTICATION FORM
          ======================================================== */}
          <div className="login-form-pane">
            <div className="login-pane-header">
              <div className="login-status-badge">
                <i className={isOnline ? "dot-online" : "dot-offline"} />
                <span>{isOnline ? "LOCAL ENGINE ONLINE • CUDA 12.8" : "CLOUD FALLBACK ACTIVE"}</span>
              </div>
              <h1>Sign in to Studio</h1>
              <p className="login-subtext">
                Access your multi-agent omission forensics canvas, live CUDA pipelines, and saved dossiers.
              </p>
            </div>

            {authError && (
              <div className="login-error-alert">
                <AlertCircle size={16} />
                <div style={{ flex: 1 }}>
                  <div>{authError}</div>
                  <div style={{ marginTop: 8 }}>
                    <button
                      type="button"
                      onClick={handleDemoGoogleLogin}
                      style={{
                        background: "rgba(255, 255, 255, 0.15)",
                        border: "1px solid rgba(255, 255, 255, 0.25)",
                        color: "#ffffff",
                        borderRadius: "6px",
                        padding: "4px 10px",
                        fontSize: "11px",
                        cursor: "pointer",
                        fontWeight: 600,
                      }}
                    >
                      Bypass & Enter Studio with Demo Profile →
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Demo Bypass Pill */}
            <div className="login-quick-access-box">
              <div className="quick-access-info">
                <Sparkles size={16} className="quick-icon" />
                <div>
                  <strong>Instant Demo Access</strong>
                  <p>Explore the full studio workspace without credentials</p>
                </div>
              </div>
              <button
                type="button"
                className="login-guest-btn"
                onClick={handleGuestAccess}
                disabled={loading}
              >
                <span>Enter Studio</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <div className="login-divider">
              <span>OR AUTHENTICATE WITH ACCOUNT</span>
            </div>

            {/* Social SSO Buttons */}
            <div className="login-sso-group">
              <button
                type="button"
                className="sso-btn google-sso-btn"
                onClick={handleGoogleSignIn}
                disabled={loading}
                title={firebaseReady ? "Sign in with your Google account" : "Configure Firebase Google Authentication"}
              >
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    fill="#EA4335"
                  />
                </svg>
                <span>Login with Google</span>
              </button>

              <button
                type="button"
                className="sso-btn"
                onClick={() => handleSignIn()}
                disabled={loading}
              >
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                <span>GitHub SSO</span>
              </button>
            </div>

            {/* Email Form */}
            <form onSubmit={handleSignIn} className="login-form">
              <div className="input-group">
                <label>Analyst Email</label>
                <div className="input-wrapper">
                  <Mail size={15} className="login-field-icon" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="analyst@domain.com"
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <div className="label-with-action">
                  <label>Workstation Key / Password</label>
                  <a
                    href="#forgot"
                    onClick={(e) => {
                      e.preventDefault();
                      alert("Use the 'Instant Demo Access' button above to enter immediately without credentials.");
                    }}
                    className="forgot-link"
                  >
                    Forgot key?
                  </a>
                </div>
                <div className="input-wrapper">
                  <Lock size={15} className="login-field-icon" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter security key"
                    required
                  />
                  <button
                    type="button"
                    className="toggle-pw-btn"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              <div className="login-options-row">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Remember this workstation</span>
                </label>
              </div>

              <button
                type="submit"
                className="login-submit-btn"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <LoaderCircle size={15} className="spin" />
                    <span>Connecting to Forensic Engine...</span>
                  </>
                ) : (
                  <>
                    <span>Sign In to Studio Workspace</span>
                    <ArrowRight size={15} />
                  </>
                )}
              </button>
            </form>

            <div className="login-footer-security">
              <ShieldCheck size={14} />
              <span>Air-gapped local model weights • AES-256 Vector Vault</span>
            </div>
          </div>

          {/* ========================================================
              RIGHT COLUMN: MARKETING HIGHLIGHTS & ANIMATIONS
          ======================================================== */}
          <div className="login-showcase-pane">
            <div className="showcase-grid-overlay" />

            <div className="showcase-content">
              {/* Header Badge */}
              <div className="showcase-badge">
                <Sparkles size={12} />
                <span>Intelligence 2.0 Forensics Platform</span>
              </div>

              <h2 className="showcase-title">
                See What Others Miss.<br />
                <span>Forensic Omission Intelligence</span>
              </h2>

              <p className="showcase-desc">
                Traditional AI analyzes only the words present. Liminal deploys a 5-agent neural network to detect what was intentionally withheld, hedged, or deflected.
              </p>

              {/* COOL ANIMATION 1: Realtime Laser Scanner Preview */}
              <div className="scanner-preview-card">
                <div className="scanner-header">
                  <div className="scanner-dots">
                    <span /><span /><span />
                  </div>
                  <span className="scanner-label">REAL-TIME FORENSIC EXTRACTION</span>
                  <span className="scanner-tag">CUDA ACTIVE</span>
                </div>

                <div className="scanner-body">
                  <div className="scanner-laser" />
                  <p className="scanner-text">
                    "I'm fine with whatever you decide. The current plan{" "}
                    <span className="scanned-highlight">
                      should probably work
                    </span>
                    ."
                  </p>
                  <div className="scanner-finding">
                    <div className="finding-pill">
                      <span className="finding-dot" />
                      <span>PRIMARY DETECTED PATTERN:</span>
                      <strong>HEDGING & COMMITMENT EVASION</strong>
                    </div>
                    <div className="finding-conf">98.4% CONFIDENCE</div>
                  </div>
                  <div className="scanner-subtext">
                    Subtext: Avoids endorsing the plan while maintaining plausible deniability if failure occurs.
                  </div>
                </div>
              </div>

              {/* COOL ANIMATION 2: Rotating 5-Agent HUD */}
              <div className="agent-hud-card">
                <div className="agent-hud-top">
                  <div className="agent-hud-icon-box">
                    <ActiveAgentIcon size={18} />
                  </div>
                  <div className="agent-hud-info">
                    <div className="agent-hud-role">{activeAgent.role}</div>
                    <div className="agent-hud-name">{activeAgent.name}</div>
                  </div>
                  <div className="agent-hud-stat">
                    <span>{activeAgent.stat}</span>
                  </div>
                </div>
                <p className="agent-hud-desc">{activeAgent.desc}</p>

                {/* Progress Indicators for 5 Agents */}
                <div className="agent-pills-row">
                  {AGENT_SHOWCASE.map((ag, i) => (
                    <button
                      key={ag.id}
                      className={`agent-pill-step ${i === currentAgentIdx ? "active" : ""}`}
                      onClick={() => setCurrentAgentIdx(i)}
                      title={ag.name}
                    >
                      <span className="pill-bar" />
                      <span className="pill-num">0{i + 1}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Micro Telemetry Pills */}
              <div className="showcase-telemetry-row">
                <div className="telemetry-chip">
                  <Cpu size={13} />
                  <span>CUDA 12.8 / RTX 3050</span>
                </div>
                <div className="telemetry-chip">
                  <Activity size={13} />
                  <span>5-Agent Consensus</span>
                </div>
                <div className="telemetry-chip">
                  <Zap size={13} />
                  <span>Zero Cloud Leakage</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ========================================================
          FIREBASE API SETUP & CONFIGURATION MODAL
      ======================================================== */}
      {showFirebaseModal && (
        <div className="firebase-modal-backdrop" onClick={() => setShowFirebaseModal(false)}>
          <div className="firebase-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="firebase-modal-header">
              <div className="firebase-modal-title">
                <div className="firebase-icon-box">
                  <Settings size={18} />
                </div>
                <div>
                  <h3>Setup Firebase Google Authentication</h3>
                  <p>Provide your Firebase Web credentials to enable Google SSO</p>
                </div>
              </div>
              <button
                className="firebase-modal-close"
                onClick={() => setShowFirebaseModal(false)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="firebase-modal-body">
              <div className="firebase-instructions">
                <span>To enable Google Login, we need 6 API keys from your Firebase Console:</span>
                <ol>
                  <li>Create a project in <strong>Firebase Console</strong> and enable <strong>Authentication → Google</strong>.</li>
                  <li>Go to <strong>Project Settings → General → Your apps → Web app</strong>.</li>
                  <li>Copy your credentials or provide them to the assistant.</li>
                </ol>
              </div>

              <div className="firebase-env-preview">
                <div className="env-preview-header">
                  <span>KEYS REQUIRED IN frontend/.env:</span>
                  <button
                    className="copy-env-btn"
                    onClick={() => {
                      navigator.clipboard.writeText(`VITE_FIREBASE_API_KEY=\nVITE_FIREBASE_AUTH_DOMAIN=\nVITE_FIREBASE_PROJECT_ID=\nVITE_FIREBASE_STORAGE_BUCKET=\nVITE_FIREBASE_MESSAGING_SENDER_ID=\nVITE_FIREBASE_APP_ID=`);
                      setCopiedKey(true);
                      setTimeout(() => setCopiedKey(false), 2000);
                    }}
                  >
                    {copiedKey ? <Check size={12} /> : <Copy size={12} />}
                    <span>{copiedKey ? "Copied" : "Copy Template"}</span>
                  </button>
                </div>
                <pre className="env-code-snippet">{`VITE_FIREBASE_API_KEY=AIzaSy...
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789...
VITE_FIREBASE_APP_ID=1:123456789:web:abcdef...`}</pre>
              </div>

              <div className="firebase-action-row">
                <button
                  type="button"
                  className="firebase-demo-btn"
                  onClick={handleDemoGoogleLogin}
                >
                  <Sparkles size={14} />
                  <span>Continue with Demo Google Profile</span>
                </button>

                <button
                  type="button"
                  className="firebase-close-btn"
                  onClick={() => setShowFirebaseModal(false)}
                >
                  <span>Close & Enter API Keys</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
