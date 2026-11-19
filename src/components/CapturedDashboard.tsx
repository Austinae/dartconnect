import { useEffect, useRef } from "react";
import { createRoot, type Root } from "react-dom/client";
import TrendChartPanel from "./TrendChartPanel";
import shellBefore from "../generated/shell-before-chart.html?raw";
import shellAfter from "../generated/shell-after-chart.html?raw";

/**
 * Static HTML shell from a one-time dashboard capture + vendored CSS.
 * Chart data is local only (no DartConnect API).
 */
export default function CapturedDashboard() {
  const rootRef = useRef<Root | null>(null);

  useEffect(() => {
    const host = document.getElementById("react-trend-chart-root");
    if (!host) return;

    rootRef.current = createRoot(host);
    rootRef.current.render(<TrendChartPanel embedded />);

    return () => {
      rootRef.current?.unmount();
      rootRef.current = null;
    };
  }, []);

  return (
    <>
      <div dangerouslySetInnerHTML={{ __html: shellBefore }} />
      <div dangerouslySetInnerHTML={{ __html: shellAfter }} />
    </>
  );
}