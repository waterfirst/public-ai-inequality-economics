import { useEffect, useMemo, useState } from "react";
import {
  Activity, BookOpen, ChevronRight, CircleAlert, Download, FlaskConical,
  Network, Pause, Play, RefreshCcw, ShieldCheck, SlidersHorizontal, Upload,
} from "lucide-react";
import { InequalityWorld } from "./components/InequalityWorld";
import { TrajectoryChart } from "./components/TrajectoryChart";
import {
  comparePolicies, DEFAULT_ENVIRONMENT, incomeHistogram, POLICIES, runSimulation,
} from "./simulation/model";
import type { Environment, Metrics, PersonaProfile, PolicyKey } from "./simulation/types";

const CONTROLS: Array<{ key: keyof Environment; label: string; hint: string; min: number; max: number; step: number }> = [
  { key: "premiumGap", label: "프리미엄 품질격차", hint: "무료·공공 모델과 고가 모델의 성능차", min: 0, max: 1.05, step: 0.01 },
  { key: "reallocationSpeed", label: "직무 대체압력", hint: "AI 노출 직무의 소득·고용 충격", min: 0, max: 0.1, step: 0.002 },
  { key: "juniorDisplacement", label: "청년 경력사다리 충격", hint: "초급 정형업무 자동화의 추가 충격", min: 0, max: 0.1, step: 0.002 },
  { key: "networkSpillover", label: "사회학습 확산", hint: "동료 네트워크를 통한 활용역량 전파", min: 0, max: 0.12, step: 0.002 },
  { key: "capitalReturn", label: "AI 자본수익률", hint: "데이터·컴퓨트·조직자본의 보상", min: 0.01, max: 0.12, step: 0.002 },
  { key: "ruralPenalty", label: "비수도권 실효접근 페널티", hint: "인프라가 아닌 교육·조직지원의 지역차", min: 0, max: 0.35, step: 0.01 },
];

const fmt = (value: number, digits = 3) => value.toFixed(digits);
const percent = (value: number, digits = 1) => `${(value * 100).toFixed(digits)}%`;

function App() {
  const [policyKey, setPolicyKey] = useState<PolicyKey>("targeted");
  const [environment, setEnvironment] = useState(DEFAULT_ENVIRONMENT);
  const [period, setPeriod] = useState(15);
  const [playing, setPlaying] = useState(false);
  const [metric, setMetric] = useState<keyof Metrics>("wolfson");
  const [profile, setProfile] = useState<PersonaProfile>();
  const [profileError, setProfileError] = useState("");

  const runs = useMemo(() => comparePolicies(environment, 2026, profile), [environment, profile]);
  const run = useMemo(() => runs.find((item) => item.policy.key === policyKey)
    ?? runSimulation({ policy: POLICIES[policyKey], environment, profile }), [runs, policyKey, environment, profile]);
  const market = runs.find((item) => item.policy.key === "market")!;
  const snapshot = run.snapshots[period];
  const initial = run.snapshots[0].metrics;
  const finalMarket = market.snapshots[period].metrics;
  const histogram = incomeHistogram(snapshot.agents);
  const maxBin = Math.max(...histogram.map((item) => item.count));

  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setPeriod((value) => value >= 15 ? 0 : value + 1), 720);
    return () => window.clearInterval(timer);
  }, [playing]);

  const setParameter = (key: keyof Environment, value: number) => {
    setPlaying(false); setPeriod(15); setEnvironment((current) => ({ ...current, [key]: value }));
  };

  const loadProfile = async (file?: File) => {
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text()) as PersonaProfile;
      if (!Array.isArray(parsed.strata) || !parsed.strata.length || !parsed.sampleSize) throw new Error("집계 strata가 없습니다.");
      setProfile(parsed); setProfileError(""); setPeriod(15);
    } catch (error) {
      setProfileError(`프로필을 읽지 못했습니다: ${(error as Error).message}`);
    }
  };

  const exportCsv = () => {
    const header = "period,gini,wolfson,atkinson,middle_share,skill_gap,capital_top10,output,ede,adoption\n";
    const rows = run.snapshots.map(({ metrics: item }) => [
      item.period, item.gini, item.wolfson, item.atkinson, item.middleShare,
      item.skillGap, item.capitalTop10, item.output, item.ede, item.adoption,
    ].join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([header + rows], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = `${policyKey}-trajectory.csv`; anchor.click(); URL.revokeObjectURL(url);
  };

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top"><span className="brand-mark"><Network size={19} /></span><span>PUBLIC AI <b>POLICY LAB</b></span></a>
        <nav><a href="#simulator">시뮬레이터</a><a href="#evidence">한국 근거</a><a href="#policy">정책 설계</a><a href="https://github.com/waterfirst/public-ai-inequality-economics/blob/main/Public_AI_Social_Infrastructure_Economics_Working_Paper_2026-08-09.pdf">논문</a></nav>
        <span className="research-badge"><span /> RESEARCH BUILD 2026</span>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow"><FlaskConical size={15} /> COMPUTATIONAL SOCIAL PHYSICS · KOREA</div>
        <h1>AI를 무상으로 나누어주면<br /><em>양극화는 사라질까?</em></h1>
        <p className="hero-copy">접근권은 출발선일 뿐입니다. 프리미엄 품질, 활용역량, 직무 전환, 지역, 돌봄, AI 자본소유가 결합되면 같은 AI를 받아도 경제적 귀결은 달라집니다.</p>
        <div className="hero-thesis"><CircleAlert size={19} /><div><b>핵심 가설</b><span>무상 접근만으로는 충분하지 않다. 역량·전환·소유를 함께 바꾸는 정밀 정책이 필요하다.</span></div></div>
        <div className="hero-stats">
          <div><strong>51%</strong><span>AI 고노출 일자리 종사자</span><small>한국은행, 2025</small></div>
          <div><strong>27%</strong><span>고노출·저보완 위험군</span><small>한국은행, 2025</small></div>
          <div><strong>1M</strong><span>NVIDIA 한국 페르소나 레코드</span><small>CC BY 4.0, 2026</small></div>
        </div>
      </section>

      <section className="lab" id="simulator">
        <div className="section-heading"><div><span>01 · INTERACTIVE LAB</span><h2>정책을 바꾸고, 사회의 궤적을 관찰하세요</h2></div><p>점은 가구, 선은 사회학습 연결입니다. 가로는 초기 자원, 세로는 소득 변화, 깊이는 권역을 나타냅니다.</p></div>
        <div className="lab-grid">
          <aside className="control-panel">
            <div className="panel-head"><div><SlidersHorizontal size={18} /><b>정책 시나리오</b></div><button onClick={() => { setEnvironment(DEFAULT_ENVIRONMENT); setPeriod(15); }}><RefreshCcw size={15} />초기화</button></div>
            <div className="policy-list">
              {(Object.keys(POLICIES) as PolicyKey[]).map((key) => (
                <button key={key} className={policyKey === key ? "selected" : ""} onClick={() => { setPolicyKey(key); setPeriod(15); setPlaying(false); }}>
                  <span className={`policy-dot ${key}`} /><span><b>{POLICIES[key].shortName}</b><small>{POLICIES[key].name}</small></span><ChevronRight size={15} />
                </button>
              ))}
            </div>
            <div className="policy-description"><b>{run.policy.name}</b><p>{run.policy.description}</p></div>
            <div className="control-title">환경 파라미터</div>
            <div className="sliders">
              {CONTROLS.map((control) => <label key={control.key}><span><b>{control.label}</b><output>{environment[control.key].toFixed(control.step < 0.01 ? 3 : 2)}</output></span><input type="range" min={control.min} max={control.max} step={control.step} value={environment[control.key]} onChange={(event) => setParameter(control.key, Number(event.target.value))} /><small>{control.hint}</small></label>)}
            </div>
            <label className="upload-box"><Upload size={18} /><span><b>NVIDIA Korea 집계 프로필</b><small>{profile ? `${profile.source} · n=${profile.sampleSize.toLocaleString()}` : "전처리 JSON을 불러와 추가 실험"}</small></span><input type="file" accept="application/json" onChange={(event) => loadProfile(event.target.files?.[0])} /></label>
            {profileError && <p className="upload-error">{profileError}</p>}
          </aside>

          <div className="visual-panel">
            <div className="world-shell">
              <InequalityWorld agents={snapshot.agents} edges={run.edges} period={period} />
              <div className="world-top"><span><i /> {run.sourceLabel}</span><span>T = {period.toString().padStart(2, "0")} / 15</span></div>
              <div className="world-legend"><span><i className="low" />하위 자원층</span><span><i className="middle" />중간층</span><span><i className="high" />상위 자원층</span><span><i className="loss" />소득 감소</span></div>
              <div className="world-controls"><button onClick={() => setPlaying((value) => !value)}>{playing ? <Pause size={16} /> : <Play size={16} />}{playing ? "일시정지" : "시간 재생"}</button><input aria-label="모형 시점" type="range" min="0" max="15" value={period} onChange={(event) => { setPlaying(false); setPeriod(Number(event.target.value)); }} /></div>
            </div>
            <div className="metric-grid">
              <MetricCard label="Wolfson 양극화" value={fmt(snapshot.metrics.wolfson)} delta={snapshot.metrics.wolfson - initial.wolfson} market={snapshot.metrics.wolfson - finalMarket.wolfson} inverse />
              <MetricCard label="중간층 비중" value={percent(snapshot.metrics.middleShare)} delta={snapshot.metrics.middleShare - initial.middleShare} market={snapshot.metrics.middleShare - finalMarket.middleShare} />
              <MetricCard label="AI 역량 격차" value={percent(snapshot.metrics.skillGap)} delta={snapshot.metrics.skillGap - initial.skillGap} market={snapshot.metrics.skillGap - finalMarket.skillGap} inverse />
              <MetricCard label="평균소득 지수" value={fmt(snapshot.metrics.output, 2)} delta={snapshot.metrics.output - initial.output} market={snapshot.metrics.output - finalMarket.output} />
            </div>
          </div>
        </div>

        <div className="analysis-grid">
          <div className="analysis-card wide">
            <div className="metric-tabs">{(["wolfson", "middleShare", "skillGap", "capitalTop10", "output"] as Array<keyof Metrics>).map((key) => <button className={metric === key ? "active" : ""} onClick={() => setMetric(key)} key={key}>{({ wolfson: "양극화", middleShare: "중간층", skillGap: "역량격차", capitalTop10: "자본집중", output: "소득" } as Record<string, string>)[key]}</button>)}</div>
            <TrajectoryChart runs={runs} metric={metric} active={policyKey} />
          </div>
          <div className="analysis-card distribution">
            <div className="chart-title"><span>소득 분포</span><small>로그소득 12구간</small></div>
            <div className="histogram">{histogram.map((item, index) => <div key={index}><span style={{ height: `${Math.max(3, item.count / maxBin * 100)}%` }} /><small>{index === 0 || index === histogram.length - 1 ? item.x.toFixed(1) : ""}</small></div>)}</div>
            <div className="distribution-note"><Activity size={17} /><p>시장 기준 대비 양극화 <b className={snapshot.metrics.wolfson <= finalMarket.wolfson ? "good" : "bad"}>{snapshot.metrics.wolfson <= finalMarket.wolfson ? "완화" : "악화"} {Math.abs(snapshot.metrics.wolfson - finalMarket.wolfson).toFixed(3)}</b></p></div>
            <button className="export" onClick={exportCsv}><Download size={16} />현재 정책 경로 CSV</button>
          </div>
        </div>
      </section>

      <section className="evidence" id="evidence">
        <div className="section-heading light"><div><span>02 · EVIDENCE LAYER</span><h2>한국 자료로 무엇을 검증하는가</h2></div><p>합성 페르소나는 표본 설계와 민감도 분석에 쓰되, 정책 효과의 인과 추정치로 해석하지 않습니다.</p></div>
        <div className="evidence-grid">
          <Evidence icon={<Activity />} number="63.5%" title="생성형 AI 이용률" text="한국 근로자 대표 가계조사. 업무 이용률은 51.8%, 평균 업무시간은 3.8% 단축." source="한국은행 이슈노트 2025-22" />
          <Evidence icon={<Network />} number="31%" title="고노출·고보완 직업 이동" text="2009~2022년 평균 전환률. 저학력과 50세 이상 대졸자의 전환 제약이 큼." source="한국은행 이슈노트 2025-2" />
          <Evidence icon={<ShieldCheck />} number="7M" title="한국어 합성 페르소나" text="1백만 레코드에 직업·연령·교육·17개 시도 맥락. 결합분포 독립성은 별도 감사 필요." source="NVIDIA Nemotron-Personas-Korea" />
        </div>
        <div className="data-guardrail"><ShieldCheck size={24} /><div><b>NVIDIA 데이터 사용 원칙</b><p>개인 이름·서술문은 저장하지 않고 연령×성별×지역×교육×직업 집계만 사용합니다. NVIDIA 데이터 카드가 밝힌 변수 간 독립성 가정 때문에 KOSIS·KLIPS 결합분포와 교차검증하며, 실제 국민 여론을 대신하는 ‘실리콘 표본’으로 사용하지 않습니다.</p></div></div>
      </section>

      <section className="policy-section" id="policy">
        <div className="section-heading"><div><span>03 · POLICY ARCHITECTURE</span><h2>무상 제공 이후의 5개 정책층</h2></div><p>양극화 해소는 서비스 가격보다 실질 활용능력과 전환비용, 생산자산의 소유구조에 달려 있습니다.</p></div>
        <div className="policy-architecture">
          {[
            ["01", "보편적 AI 권리", "기본 추론량·접근성·다중 모델 선택권", "접근률"],
            ["02", "역량 기반 교육", "저역량층·청년·고령층 맞춤형 직무 훈련", "무도구 사후성과"],
            ["03", "직무전환 보험", "전환수당·기업 내 경력사다리·지역훈련", "고보완 직무 이동률"],
            ["04", "돌봄·행정 지원", "취약가구의 시간 제약과 서비스 탐색비용 완화", "오류·이의제기·고용"],
            ["05", "AI 자본의 시민 몫", "연기금·근로자 지분·공공 컴퓨트 배당", "자본소득 상위 집중"],
          ].map(([no, title, text, kpi]) => <article key={no}><span>{no}</span><div><h3>{title}</h3><p>{text}</p><small>KPI · {kpi}</small></div></article>)}
        </div>
        <div className="conclusion-band"><BookOpen size={25} /><div><span>논문의 정책 결론</span><h3>“무상 AI”가 아니라 <em>역량·시간·교섭력·자본청구권</em>을 늘리는 공공 AI여야 한다.</h3></div><a href="https://github.com/waterfirst/public-ai-inequality-economics">연구 저장소 <ChevronRight size={16} /></a></div>
      </section>

      <footer><p>Public AI as Social Infrastructure · Nak Cho Choi · 2026</p><p>모든 수치는 모형 조건부 비교정학이며 예측·인과효과가 아닙니다.</p></footer>
    </main>
  );
}

function MetricCard({ label, value, delta, market, inverse = false }: { label: string; value: string; delta: number; market: number; inverse?: boolean }) {
  const better = inverse ? market <= 0 : market >= 0;
  return <article><span>{label}</span><strong>{value}</strong><small>초기 대비 {delta >= 0 ? "+" : ""}{delta.toFixed(3)}</small><em className={better ? "good" : "bad"}>시장 대비 {market >= 0 ? "+" : ""}{market.toFixed(3)}</em></article>;
}

function Evidence({ icon, number, title, text, source }: { icon: React.ReactNode; number: string; title: string; text: string; source: string }) {
  return <article><div className="evidence-icon">{icon}</div><strong>{number}</strong><h3>{title}</h3><p>{text}</p><small>{source}</small></article>;
}

export default App;
