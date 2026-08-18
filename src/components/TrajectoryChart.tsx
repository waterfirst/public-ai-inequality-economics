import type { Metrics, PolicyKey, SimulationRun } from "../simulation/types";

const COLORS: Record<PolicyKey, string> = {
  market: "#ff6b6b", free: "#77a8ff", education: "#f6c45b",
  targeted: "#54e5cb", comprehensive: "#a88bff", failed: "#8c9bad",
};

const LABELS: Partial<Record<keyof Metrics, string>> = {
  wolfson: "Wolfson 양극화", gini: "Gini", middleShare: "중간층 비중",
  skillGap: "AI 역량 격차", capitalTop10: "상위 10% 자본몫", output: "평균소득",
};

type Props = { runs: SimulationRun[]; metric: keyof Metrics; active: PolicyKey };

export function TrajectoryChart({ runs, metric, active }: Props) {
  const width = 720; const height = 260; const padding = 34;
  const values = runs.flatMap((run) => run.snapshots.map((snapshot) => Number(snapshot.metrics[metric])));
  const min = Math.min(...values); const max = Math.max(...values); const span = max - min || 1;
  const x = (index: number, count: number) => padding + index * (width - padding * 2) / Math.max(1, count - 1);
  const y = (value: number) => height - padding - (value - min) * (height - padding * 2) / span;
  const lines = runs.map((run) => ({
    key: run.policy.key,
    name: run.policy.shortName,
    path: run.snapshots.map((snapshot, index) => `${index ? "L" : "M"}${x(index, run.snapshots.length).toFixed(1)},${y(Number(snapshot.metrics[metric])).toFixed(1)}`).join(" "),
  }));
  return (
    <div className="chart-wrap">
      <div className="chart-title"><span>{LABELS[metric] ?? metric}</span><small>모형 시점별 정책 경로</small></div>
      <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${LABELS[metric] ?? metric} 정책 비교 그래프`}>
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const gy = padding + ratio * (height - padding * 2);
          const value = max - ratio * span;
          return <g key={ratio}><line x1={padding} x2={width - padding} y1={gy} y2={gy} stroke="#17324a" /><text x={padding - 7} y={gy + 3} textAnchor="end">{value.toFixed(value < 1 ? 3 : 2)}</text></g>;
        })}
        {lines.map((line) => <path key={line.key} d={line.path} fill="none" stroke={COLORS[line.key]} strokeWidth={line.key === active ? 3.5 : 1.5} opacity={line.key === active ? 1 : 0.45} />)}
      </svg>
      <div className="chart-legend">{lines.map((line) => <span className={line.key === active ? "active" : ""} key={line.key}><i style={{ background: COLORS[line.key] }} />{line.name}</span>)}</div>
    </div>
  );
}
