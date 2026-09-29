import { useEffect, useState } from "react";

const GLYPHS = "01_/*#@%[]<>-=+$~";

export default function DecryptedText({
  text,
  speed = 40,
  maxIterations = 12,
  className = "",
  animateOnMount = true,
}) {
  const [displayText, setDisplayText] = useState(text);
  const [isHovered, setIsHovered] = useState(false);

  const triggerScramble = () => {
    let iteration = 0;
    const interval = setInterval(() => {
      setDisplayText(() =>
        text
          .split("")
          .map((char, index) => {
            if (char === " " || char === "\n") return char;
            if (index < iteration) {
              return text[index];
            }
            return GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          })
          .join("")
      );

      if (iteration >= text.length) {
        clearInterval(interval);
      }
      iteration += 1 / (maxIterations / text.length || 1);
    }, speed);

    return () => clearInterval(interval);
  };

  useEffect(() => {
    if (animateOnMount) {
      const cleanup = triggerScramble();
      return cleanup;
    }
  }, [text, animateOnMount]);

  return (
    <span
      className={`decrypted-text ${className}`}
      onMouseEnter={() => {
        if (!isHovered) {
          setIsHovered(true);
          triggerScramble();
          setTimeout(() => setIsHovered(false), 1200);
        }
      }}
    >
      {displayText}
    </span>
  );
}
