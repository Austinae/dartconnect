export type PlayType =
  | "Social"
  | "DartBot"
  | "Lobbies"
  | "Events"
  | "League Singles"
  | "League Team";

export type GameType = "Singles 501 SIDO" | "Singles Cricket";

export type TimeRange = "14d" | "30d" | "90d" | "season" | "all";

export type ChartMode = "match" | "rolling";

export interface PerformancePoint {
  id: string;
  date: string;
  threeDartAvg: number;
  playType: PlayType;
  gameType: GameType;
  opponent?: string;
  result?: string;
  synthetic?: boolean;
  personalBest?: boolean;
  report?: string;
}

export const PLAY_TYPE_COLORS: Record<PlayType, string> = {
  Social: "#ee9e4e",
  DartBot: "#7fcfeb",
  Lobbies: "#57a0c3",
  Events: "#e97c34",
  "League Singles": "#898989",
  "League Team": "#577387",
};

export const ALL_PLAY_TYPES: PlayType[] = [
  "League Team",
  "League Singles",
  "Social",
  "DartBot",
  "Lobbies",
  "Events",
];