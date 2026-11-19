import type { PerformancePoint } from "../types";
import points from "./performances.json";

export const PLAYER = {
  name: "William Guerrand",
  memberNumber: 368894,
  league: "New York Dart League – Tuesday – Fall 2026",
  team: "3 20's walk into a bar",
  seasonStart: "2026-08-15",
} as const;

export const performances = points as PerformancePoint[];