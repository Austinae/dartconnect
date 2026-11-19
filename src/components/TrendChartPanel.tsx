import { useMemo, useState } from "react";
import {
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import { performances } from "../data/performances";
import {
  ALL_PLAY_TYPES,
  PLAY_TYPE_COLORS,
  type ChartMode,
  type PlayType,
  type TimeRange,
} from "../types";
import { buildChartRows, filterPoints, periodStats, rangeLabel } from "../lib/chart";

const TIME_RANGES: { id: TimeRange; label: string }[] = [
  { id: "14d", label: "2W" },
  { id: "30d", label: "1M" },
  { id: "90d", label: "3M" },
  { id: "season", label: "Season" },
  { id: "all", label: "All" },
];

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: ReturnType<typeof buildChartRows>[number] }[];
}) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  return (
    <div
      className="rounded-md px-3 py-2 text-xs text-white shadow-lg"
      style={{ background: "#0b141d" }}
    >
      <div className="font-semibold">{row.date}</div>
      <div className="font-montserrat text-lg font-bold">{row.avg.toFixed(2)}</div>
      <div className="opacity-90">{row.playType}</div>
      {row.opponent && <div className="opacity-80">{row.opponent}</div>}
      {row.personalBest && (
        <div className="mt-1 font-semibold text-yellow-400">Personal best</div>
      )}
      {row.synthetic && (
        <div className="mt-0.5 text-[10px] opacity-70">Illustrative practice session</div>
      )}
    </div>
  );
}

export default function TrendChartPanel({ embedded = false }: { embedded?: boolean }) {
  const [range, setRange] = useState<TimeRange>("season");
  const [mode, setMode] = useState<ChartMode>("rolling");
  const [playTypes, setPlayTypes] = useState<Set<PlayType>>(
    () => new Set(ALL_PLAY_TYPES)
  );

  const filtered = useMemo(
    () => filterPoints(performances, range, playTypes),
    [range, playTypes]
  );
  const chartRows = useMemo(() => buildChartRows(filtered, mode), [filtered, mode]);
  const stats = useMemo(() => periodStats(filtered), [filtered]);

  const yDomain = useMemo(() => {
    const values = chartRows.flatMap((r) =>
      [r.avg, r.rolling].filter((v): v is number => v != null)
    );
    if (values.length === 0) return [20, 55] as [number, number];
    const min = Math.min(...values);
    const max = Math.max(...values);
    return [Math.floor(min - 4), Math.ceil(max + 3)] as [number, number];
  }, [chartRows]);

  const togglePlayType = (pt: PlayType) => {
    setPlayTypes((prev) => {
      const next = new Set(prev);
      if (next.has(pt)) {
        if (next.size > 1) next.delete(pt);
      } else next.add(pt);
      return next;
    });
  };

  const scatterData = chartRows.map((r) => ({ ...r, x: r.label }));
  const up = stats.delta != null && stats.delta >= 0;

  const toolbar = (
    <div className="dc-trend-toolbar mb-3 flex flex-wrap items-center justify-between gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <div className="dc-trend-range">
          {TIME_RANGES.map((t) => (
            <button
              key={t.id}
              type="button"
              className={range === t.id ? "dc-trend-on" : ""}
              onClick={() => setRange(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="dc-trend-range" style={{ background: "#fff", border: "1px solid #d6e4f1" }}>
          <button
            type="button"
            className={mode === "match" ? "dc-trend-ghost-on" : ""}
            onClick={() => setMode("match")}
          >
            Per session
          </button>
          <button
            type="button"
            className={mode === "rolling" ? "dc-trend-ghost-on" : ""}
            onClick={() => setMode("rolling")}
          >
            Rolling 5
          </button>
        </div>
      </div>
      {stats.latest != null && (
        <div className="text-right text-sm">
          <div className="font-montserrat text-2xl font-bold text-blue-500">
            {stats.latest.toFixed(2)}
          </div>
          {stats.delta != null && (
            <div className={`font-semibold ${up ? "text-green-700" : "text-red-600"}`}>
              {up ? "+" : ""}
              {stats.delta.toFixed(2)} vs start
            </div>
          )}
        </div>
      )}
    </div>
  );

  const chart = (
    <div className={embedded ? "dc-trend-chart-canvas" : "dc-trend-chart-canvas"} style={embedded ? undefined : { height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={scatterData} margin={{ top: 8, right: 8, left: 0, bottom: 4 }}>
          <CartesianGrid stroke="#d6e4f1" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: "#667b8f", fontSize: 11 }}
            axisLine={{ stroke: "#c4d8eb" }}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={yDomain}
            tick={{ fill: "#667b8f", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={32}
          />
          <ZAxis range={[80, 80]} />
          <Tooltip content={<CustomTooltip />} />
          {mode === "rolling" && (
            <Line
              type="monotone"
              dataKey="rolling"
              stroke="#25435f"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
            />
          )}
          <Scatter
            dataKey="avg"
            shape={(props: {
              cx?: number;
              cy?: number;
              payload?: (typeof scatterData)[number];
            }) => {
              const { cx = 0, cy = 0, payload } = props;
              const color = payload
                ? PLAY_TYPE_COLORS[payload.playType as PlayType]
                : "#577387";
              const r = payload?.personalBest ? 7 : 5;
              return (
                <circle
                  cx={cx}
                  cy={cy}
                  r={r}
                  fill={color}
                  stroke={payload?.personalBest ? "#ae1108" : "#fff"}
                  strokeWidth={payload?.personalBest ? 2 : 1.5}
                />
              );
            }}
          />
          {stats.high != null && (
            <ReferenceLine y={stats.high} stroke="#ae1108" strokeDasharray="4 4" opacity={0.4} />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );

  const playTypeRow = (
    <div className="dc-trend-play mt-3 flex flex-wrap gap-1.5 border-t border-coolblue-300 pt-3">
      {ALL_PLAY_TYPES.map((pt) => {
        const on = playTypes.has(pt);
        return (
          <button
            key={pt}
            type="button"
            className={on ? "dc-trend-play-on" : ""}
            onClick={() => togglePlayType(pt)}
          >
            <span
              style={{
                display: "inline-block",
                width: 8,
                height: 8,
                borderRadius: "50%",
                marginRight: 6,
                background: on ? PLAY_TYPE_COLORS[pt] : "#c4d8eb",
                verticalAlign: "middle",
              }}
            />
            {pt}
          </button>
        );
      })}
    </div>
  );

  if (embedded) {
    return (
      <div className="relative w-full px-1">
        {toolbar}
        {chart}
        {playTypeRow}
      </div>
    );
  }

  return (
    <div className="rounded-md bg-white p-4 shadow">
      <h2 className="font-montserrat text-xl font-bold text-blue-500">My 3-Dart Average Trend</h2>
      <p className="mb-2 text-sm text-blue-400">
        Singles 501 SIDO · {rangeLabel(range)} · {filtered.length} sessions
      </p>
      {toolbar}
      {chart}
      {playTypeRow}
    </div>
  );
}