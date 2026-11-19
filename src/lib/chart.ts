import type { ChartMode, PerformancePoint, TimeRange } from "../types";
import { PLAYER } from "../data/performances";

const PROTOTYPE_TODAY = new Date("2026-11-19T12:00:00");

export function parseDate(iso: string): Date {
  return new Date(`${iso}T12:00:00`);
}

export function rangeStart(range: TimeRange, points: PerformancePoint[]): Date {
  const end = PROTOTYPE_TODAY;
  switch (range) {
    case "14d":
      return addDays(end, -14);
    case "30d":
      return addDays(end, -30);
    case "90d":
      return addDays(end, -90);
    case "season":
      return parseDate(PLAYER.seasonStart);
    case "all": {
      const min = points.reduce(
        (acc, p) => Math.min(acc, parseDate(p.date).getTime()),
        end.getTime()
      );
      return new Date(min);
    }
  }
}

function addDays(d: Date, days: number): Date {
  const out = new Date(d);
  out.setDate(out.getDate() - days);
  return out;
}

export function filterPoints(
  points: PerformancePoint[],
  range: TimeRange,
  playTypes: Set<string>
): PerformancePoint[] {
  const start = rangeStart(range, points);
  return points
    .filter((p) => playTypes.has(p.playType))
    .filter((p) => parseDate(p.date) >= start && parseDate(p.date) <= PROTOTYPE_TODAY)
    .sort((a, b) => parseDate(a.date).getTime() - parseDate(b.date).getTime());
}

export interface ChartRow {
  date: string;
  label: string;
  avg: number;
  rolling?: number;
  playType: string;
  opponent?: string;
  personalBest?: boolean;
  synthetic?: boolean;
}

export function buildChartRows(
  points: PerformancePoint[],
  mode: ChartMode,
  window = 5
): ChartRow[] {
  const rows: ChartRow[] = points.map((p) => ({
    date: p.date,
    label: formatShortDate(p.date),
    avg: p.threeDartAvg,
    playType: p.playType,
    opponent: p.opponent,
    personalBest: p.personalBest,
    synthetic: p.synthetic,
  }));

  if (mode === "rolling") {
    for (let i = 0; i < rows.length; i++) {
      const slice = points.slice(Math.max(0, i - window + 1), i + 1);
      const mean = slice.reduce((s, p) => s + p.threeDartAvg, 0) / slice.length;
      rows[i].rolling = Math.round(mean * 100) / 100;
    }
  }

  return rows;
}

export function formatShortDate(iso: string): string {
  return parseDate(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

export function periodStats(points: PerformancePoint[]) {
  if (points.length === 0) {
    return { latest: null, delta: null, high: null, count: 0 };
  }
  const latest = points[points.length - 1].threeDartAvg;
  const first = points[0].threeDartAvg;
  const high = Math.max(...points.map((p) => p.threeDartAvg));
  return {
    latest,
    delta: Math.round((latest - first) * 100) / 100,
    high,
    count: points.length,
  };
}

export function rangeLabel(range: TimeRange): string {
  const labels: Record<TimeRange, string> = {
    "14d": "2 weeks",
    "30d": "1 month",
    "90d": "3 months",
    season: "Full season",
    all: "All data",
  };
  return labels[range];
}