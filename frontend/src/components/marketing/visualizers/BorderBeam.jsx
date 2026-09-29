import "./BorderBeam.css";

export default function BorderBeam({
  className = "",
  size = 220,
  duration = 8,
  delay = 0,
  colorFrom = "rgba(255, 255, 255, 0.95)",
  colorTo = "rgba(255, 255, 255, 0.0)",
}) {
  return (
    <div
      className={`border-beam-container ${className}`}
      style={{
        "--size": `${size}px`,
        "--duration": `${duration}s`,
        "--delay": `-${delay}s`,
        "--color-from": colorFrom,
        "--color-to": colorTo,
      }}
    >
      <div className="border-beam-glow" />
    </div>
  );
}
