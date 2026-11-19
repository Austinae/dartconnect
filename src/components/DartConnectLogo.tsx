/** Compact My DartConnect wordmark (simplified from live site SVG). */
export default function DartConnectLogo({ className = "h-12 w-auto" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 320 72" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="DartConnect">
      <path d="M52 4c28 5 52 24 68 52L8 52c14-32 38-46 44-48Z" fill="#ae1108" />
      <path d="M8 20h40L48 52H8V20Z" fill="#8e1212" opacity="0.85" />
      <text x="78" y="38" fill="#fff" fontFamily="Montserrat, sans-serif" fontSize="22" fontWeight="700">
        MY
      </text>
      <text x="118" y="38" fill="#fff" fontFamily="Montserrat, sans-serif" fontSize="22" fontWeight="700">
        DartConnect
      </text>
      <text x="78" y="58" fill="#f8d583" fontFamily="Montserrat, sans-serif" fontSize="11" fontWeight="600" letterSpacing="2">
        PERFECT YOUR GAME
      </text>
    </svg>
  );
}