import type {
  Agent,
  Edge,
  Environment,
  Metrics,
  Occupation,
  PersonaProfile,
  Policy,
  PolicyKey,
  SimulationRun,
} from "./types";

export const DEFAULT_ENVIRONMENT: Environment = {
  premiumGap: 0.45,
  reallocationSpeed: 0.045,
  capitalReturn: 0.065,
  feedback: 0.18,
  networkSpillover: 0.035,
  juniorDisplacement: 0.035,
  ruralPenalty: 0.12,
};

export const POLICIES: Record<PolicyKey, Policy> = {
  market: {
    key: "market", name: "시장·프리미엄 AI", shortName: "시장 기준",
    description: "소득·조직자본이 높은 집단이 고성능 AI를 우선 구매합니다.",
    publicAccess: 0.1, publicQuality: 0.3, education: 0, care: 0,
    capitalDividend: 0, workerOwnership: 0, equalizingDesign: 0, trust: 0.65,
  },
  free: {
    key: "free", name: "전 국민 무상 AI", shortName: "무상 접근",
    description: "접근권은 보편화하지만 역량·직업·자본 격차는 그대로 둡니다.",
    publicAccess: 0.98, publicQuality: 0.72, education: 0, care: 0,
    capitalDividend: 0, workerOwnership: 0, equalizingDesign: 0.1, trust: 0.82,
  },
  education: {
    key: "education", name: "무상 AI + 적응교육", shortName: "교육 결합",
    description: "저역량·전환위험 집단에 사용교육과 직무전환을 집중합니다.",
    publicAccess: 0.98, publicQuality: 0.82, education: 0.065, care: 0,
    capitalDividend: 0, workerOwnership: 0, equalizingDesign: 0.32, trust: 0.86,
  },
  targeted: {
    key: "targeted", name: "한국형 정밀 패키지", shortName: "정밀 정책",
    description: "청년·고령·지역·돌봄 취약성과 직업별 대체위험을 함께 표적화합니다.",
    publicAccess: 0.98, publicQuality: 0.86, education: 0.082, care: 0.07,
    capitalDividend: 0.26, workerOwnership: 0.12, equalizingDesign: 0.62, trust: 0.9,
  },
  comprehensive: {
    key: "comprehensive", name: "공공 AI 종합안", shortName: "종합 패키지",
    description: "접근·교육·돌봄·자본배당·근로자 소유를 모두 결합합니다.",
    publicAccess: 0.98, publicQuality: 0.9, education: 0.065, care: 0.075,
    capitalDividend: 0.22, workerOwnership: 0.08, equalizingDesign: 0.42, trust: 0.92,
  },
  failed: {
    key: "failed", name: "저품질 공공 AI", shortName: "실패 사례",
    description: "넓은 보급에도 낮은 품질·신뢰·지원이 실효 이용을 막습니다.",
    publicAccess: 0.9, publicQuality: 0.42, education: 0.018, care: 0.025,
    capitalDividend: 0, workerOwnership: 0, equalizingDesign: 0.04, trust: 0.38,
  },
};

export const OCCUPATIONS: Occupation[] = [
  { id: "ict", label: "ICT·정보서비스", exposure: 0.91, complementarity: 0.72, baseIncome: 1.42 },
  { id: "professional", label: "전문·사업서비스", exposure: 0.84, complementarity: 0.69, baseIncome: 1.34 },
  { id: "office", label: "사무·행정", exposure: 0.79, complementarity: 0.42, baseIncome: 1.02 },
  { id: "manufacturing", label: "제조·공정", exposure: 0.55, complementarity: 0.5, baseIncome: 1.08 },
  { id: "education", label: "교육·공공", exposure: 0.66, complementarity: 0.7, baseIncome: 1.12 },
  { id: "care", label: "보건·돌봄", exposure: 0.43, complementarity: 0.77, baseIncome: 0.96 },
  { id: "service", label: "판매·서비스", exposure: 0.38, complementarity: 0.43, baseIncome: 0.82 },
  { id: "manual", label: "건설·운송·현장", exposure: 0.28, complementarity: 0.51, baseIncome: 0.91 },
];

const REGIONS = ["수도권", "충청권", "호남권", "영남권", "강원·제주"];

const clamp = (value: number, min = 0, max = 1) => Math.min(max, Math.max(min, value));
const sigmoid = (value: number) => 1 / (1 + Math.exp(-Math.min(30, Math.max(-30, value))));

export function mulberry32(seed: number) {
  let value = seed >>> 0;
  return () => {
    value += 0x6d2b79f5;
    let t = value;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function normal(random: () => number) {
  return Math.sqrt(-2 * Math.log(Math.max(1e-12, random()))) * Math.cos(2 * Math.PI * random());
}

function weightedIndex(random: () => number, weights: number[]) {
  const total = weights.reduce((sum, value) => sum + value, 0);
  let target = random() * total;
  for (let index = 0; index < weights.length; index += 1) {
    target -= weights[index];
    if (target <= 0) return index;
  }
  return weights.length - 1;
}

function parseAgeGroup(value: string | undefined, random: () => number) {
  const match = value?.match(/(\d{2})\D+(\d{2})/);
  if (match) return Number(match[1]) + Math.floor(random() * (Number(match[2]) - Number(match[1]) + 1));
  const single = value?.match(/(\d{2})/);
  if (single) return clamp(Number(single[1]) + Math.floor(random() * 10), 19, 89);
  return 19 + weightedIndex(random, [0.14, 0.17, 0.2, 0.24, 0.16, 0.09]) * 10 + Math.floor(random() * 10);
}

function occupationFromText(value: string | undefined, random: () => number) {
  if (!value) return OCCUPATIONS[weightedIndex(random, [0.07, 0.1, 0.19, 0.19, 0.1, 0.1, 0.13, 0.12])];
  const text = value.toLowerCase();
  const rules: Array<[RegExp, string]> = [
    [/개발|소프트웨어|정보|데이터|통신|computer|software|data/, "ict"],
    [/연구|법|회계|금융|경영|전문|research|law|finance/, "professional"],
    [/사무|행정|관리|office|administr/, "office"],
    [/제조|기술|엔지니어|생산|manufact|engineer/, "manufacturing"],
    [/교육|교사|교수|공무|teach|education|public/, "education"],
    [/의료|간호|보건|복지|돌봄|health|care/, "care"],
    [/판매|서비스|요리|숙박|service|sales|food/, "service"],
  ];
  const id = rules.find(([pattern]) => pattern.test(text))?.[1] ?? "manual";
  return OCCUPATIONS.find((item) => item.id === id)!;
}

function sampleStratum(profile: PersonaProfile | undefined, random: () => number) {
  if (!profile?.strata.length) return undefined;
  return profile.strata[weightedIndex(random, profile.strata.map((item) => item.count))];
}

export function buildPopulation(seed = 2026, size = 420, profile?: PersonaProfile) {
  const random = mulberry32(seed);
  const drafts = Array.from({ length: size }, (_, id) => {
    const stratum = sampleStratum(profile, random);
    const age = parseAgeGroup(stratum?.ageGroup, random);
    const female = stratum?.sex ? /여|female|woman/i.test(stratum.sex) : random() < (age >= 70 ? 0.57 : 0.5);
    const regionIndex = stratum?.region
      ? Math.max(0, REGIONS.findIndex((region) => stratum.region!.includes(region.slice(0, 2))))
      : weightedIndex(random, [0.51, 0.11, 0.1, 0.24, 0.04]);
    const region = REGIONS[regionIndex < 0 ? 0 : regionIndex];
    const rural = region !== "수도권" && random() < (region === "강원·제주" ? 0.42 : 0.22);
    const occupation = occupationFromText(stratum?.occupation, random);
    const educationText = stratum?.education?.toLowerCase() ?? "";
    const education = educationText
      ? (/박사|대학원|graduate|doctor/.test(educationText) ? 0.92 : /대학|학사|college|university/.test(educationText) ? 0.72 : /고등|high/.test(educationText) ? 0.45 : 0.3)
      : clamp(0.2 + 0.28 * occupation.complementarity + 0.18 * normal(random), 0.08, 0.98);
    const latent = 0.52 * normal(random) + 0.7 * education + 0.24 * occupation.baseIncome - 0.12 * Number(rural);
    return { id, age, female, region, rural, education, occupation, latent };
  });
  const ordered = [...drafts].sort((a, b) => a.latent - b.latent);
  const rank = new Map(ordered.map((agent, index) => [agent.id, index / Math.max(1, size - 1)]));
  const agents: Agent[] = drafts.map((draft) => {
    const resource = rank.get(draft.id)!;
    const skill = clamp(0.12 + 0.54 * draft.education + 0.26 * resource + 0.13 * normal(random), 0.03, 0.98);
    const capital = Math.exp(-1.8 + 2.2 * resource + 0.65 * normal(random));
    const labor = Math.exp(-0.18 + Math.log(draft.occupation.baseIncome) + 0.62 * resource + 0.22 * normal(random));
    const vulnerable = random() < 0.07 + 0.22 * (1 - resource) + (draft.age >= 65 ? 0.12 : 0);
    const burden = vulnerable ? 0.25 + 0.65 * random() : 0.05 * random();
    const premium = random() < sigmoid(-4.2 + 7 * resource);
    const trust = clamp(0.58 + 0.18 * normal(random) - 0.08 * Number(draft.age >= 65), 0.08, 0.96);
    const income = labor + DEFAULT_ENVIRONMENT.capitalReturn * capital;
    return {
      ...draft, resource, skill, capital, labor, income, initialIncome: income,
      flexibility: clamp(0.35 * skill + 0.28 * resource + 0.3 * random(), 0.05, 0.98),
      burden, vulnerable, premium, trust, employed: clamp(1 - 0.18 * Number(vulnerable) * burden, 0.7, 1),
      adoption: premium ? 0.78 : 0.18, effectiveAI: 0, growth: 0,
    };
  });
  return agents;
}

export function buildNetwork(agents: Agent[], seed = 2026) {
  const random = mulberry32(seed + 404);
  const edges: Edge[] = [];
  const seen = new Set<string>();
  const add = (source: number, target: number) => {
    if (source === target) return;
    const a = Math.min(source, target); const b = Math.max(source, target); const key = `${a}-${b}`;
    if (!seen.has(key)) { seen.add(key); edges.push({ source: a, target: b }); }
  };
  agents.forEach((agent, index) => {
    const candidates = agents
      .map((other, target) => ({
        target,
        score: Math.abs(agent.resource - other.resource)
          + (agent.region === other.region ? 0 : 0.45)
          + (agent.occupation.id === other.occupation.id ? 0 : 0.24)
          + random() * 0.12,
      }))
      .filter(({ target }) => target !== index)
      .sort((a, b) => a.score - b.score);
    add(index, candidates[0].target);
    add(index, candidates[1].target);
    if (random() < 0.3) add(index, Math.floor(random() * agents.length));
  });
  return edges;
}

function neighborMeans(agents: Agent[], edges: Edge[]) {
  const skill = new Float64Array(agents.length);
  const adoption = new Float64Array(agents.length);
  const count = new Uint16Array(agents.length);
  edges.forEach(({ source, target }) => {
    skill[source] += agents[target].skill; skill[target] += agents[source].skill;
    adoption[source] += agents[target].adoption; adoption[target] += agents[source].adoption;
    count[source] += 1; count[target] += 1;
  });
  return agents.map((agent, index) => ({
    skill: count[index] ? skill[index] / count[index] : agent.skill,
    adoption: count[index] ? adoption[index] / count[index] : agent.adoption,
  }));
}

function quantile(sorted: number[], q: number) {
  const position = (sorted.length - 1) * q;
  const base = Math.floor(position); const rest = position - base;
  return sorted[base] + (sorted[base + 1] !== undefined ? rest * (sorted[base + 1] - sorted[base]) : 0);
}

export function gini(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  const sum = sorted.reduce((total, value) => total + value, 0);
  if (!sum) return 0;
  const weighted = sorted.reduce((total, value, index) => total + (index + 1) * value, 0);
  return (2 * weighted) / (sorted.length * sum) - (sorted.length + 1) / sorted.length;
}

export function wolfson(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  const total = sorted.reduce((sum, value) => sum + value, 0);
  const half = sorted.length / 2;
  const whole = Math.floor(half);
  const lower = sorted.slice(0, whole).reduce((sum, value) => sum + value, 0)
    + (half - whole && sorted[whole] ? (half - whole) * sorted[whole] : 0);
  const median = quantile(sorted, 0.5);
  const mean = total / sorted.length;
  return Math.max(0, 2 * (2 * (0.5 - lower / total) - gini(sorted)) * mean / median);
}

export function calculateMetrics(agents: Agent[], period: number): Metrics {
  const income = agents.map((agent) => Math.max(1e-6, agent.income));
  const sortedIncome = [...income].sort((a, b) => a - b);
  const median = quantile(sortedIncome, 0.5);
  const mean = income.reduce((sum, value) => sum + value, 0) / income.length;
  const ede = Math.exp(income.reduce((sum, value) => sum + Math.log(value), 0) / income.length);
  const byResource = [...agents].sort((a, b) => a.resource - b.resource);
  const fifth = Math.max(1, Math.floor(agents.length * 0.2));
  const tenth = Math.max(1, Math.floor(agents.length * 0.1));
  const low = byResource.slice(0, fifth); const high = byResource.slice(-fifth);
  const capital = agents.map((agent) => agent.capital).sort((a, b) => a - b);
  const vulnerable = agents.filter((agent) => agent.vulnerable);
  const average = (values: number[]) => values.reduce((sum, value) => sum + value, 0) / Math.max(1, values.length);
  return {
    period,
    gini: gini(income),
    wolfson: wolfson(income),
    atkinson: 1 - ede / mean,
    middleShare: income.filter((value) => value >= 0.75 * median && value <= 1.25 * median).length / income.length,
    topBottomRatio: average(high.map((agent) => agent.income)) / average(low.map((agent) => agent.income)),
    skillGap: average(high.map((agent) => agent.skill)) - average(low.map((agent) => agent.skill)),
    capitalTop10: capital.slice(-tenth).reduce((sum, value) => sum + value, 0) / capital.reduce((sum, value) => sum + value, 0),
    output: mean,
    ede,
    adoption: average(agents.map((agent) => agent.adoption)),
    vulnerableEmployment: average(vulnerable.map((agent) => agent.employed)),
  };
}

function cloneAgents(agents: Agent[]) {
  return agents.map((agent) => ({ ...agent, occupation: { ...agent.occupation } }));
}

export function runSimulation({
  policy,
  environment = DEFAULT_ENVIRONMENT,
  seed = 2026,
  size = 420,
  periods = 15,
  profile,
}: {
  policy: Policy;
  environment?: Environment;
  seed?: number;
  size?: number;
  periods?: number;
  profile?: PersonaProfile;
}): SimulationRun {
  const random = mulberry32(seed + policy.key.length * 7919);
  let agents = buildPopulation(seed, size, profile);
  const edges = buildNetwork(agents, seed);
  const snapshots = [{ agents: cloneAgents(agents), metrics: calculateMetrics(agents, 0) }];
  for (let period = 1; period <= periods; period += 1) {
    const peers = neighborMeans(agents, edges);
    const profits = new Float64Array(size);
    const taxes = new Float64Array(size);
    const next = agents.map((agent, index) => {
      const publicProbability = policy.publicAccess * policy.trust * agent.trust * (1 - environment.ruralPenalty * Number(agent.rural));
      const hasPublic = random() < publicProbability;
      const quality = agent.premium ? 1 + environment.premiumGap : hasPublic ? policy.publicQuality : 0.22;
      const peerAdoption = peers[index].adoption;
      const adoption = clamp(agent.adoption + 0.22 * (hasPublic || agent.premium ? 1 : 0) + environment.networkSpillover * (peerAdoption - agent.adoption));
      const effectiveAI = quality * sigmoid(-0.8 + 2.5 * agent.skill + 1.2 * agent.flexibility) * (0.55 + 0.45 * adoption);
      const progressiveTarget = (1.15 - agent.resource) * (1 - agent.skill);
      const transitionWeight = agent.occupation.exposure * (1 - agent.occupation.complementarity);
      const educationBoost = policy.education * progressiveTarget * (1 + 0.55 * transitionWeight);
      const networkLearning = environment.networkSpillover * 0.22 * (peers[index].skill - agent.skill);
      const skill = clamp(agent.skill + educationBoost + 0.018 * effectiveAI * (1 - agent.skill) + networkLearning);
      const burden = Math.max(0, agent.burden - policy.care * Number(agent.vulnerable) * (1 - agent.burden));
      const adaptation = clamp(0.42 * skill + 0.28 * agent.flexibility + 0.3 * Math.min(effectiveAI, 1));
      const augmentation = 0.043 * agent.occupation.exposure * effectiveAI * (0.28 + 0.72 * skill)
        + 0.055 * policy.equalizingDesign * agent.occupation.exposure * Number(hasPublic) * (1 - skill) * (1 - agent.resource);
      const seniorityRisk = agent.age < 30 ? environment.juniorDisplacement * agent.occupation.exposure * (1 - agent.occupation.complementarity) : 0;
      const displacement = environment.reallocationSpeed * agent.occupation.exposure * (1 - adaptation) + seniorityRisk;
      const careRelief = 0.02 * policy.care * Number(agent.vulnerable) * (1 - burden);
      const growth = Math.min(0.18, Math.max(-0.14, augmentation - displacement + careRelief + environment.feedback * agent.growth));
      const employed = clamp(agent.employed - 0.055 * displacement + 0.05 * adaptation * policy.education + 0.03 * policy.care * Number(agent.vulnerable), 0.45, 1);
      const labor = agent.labor * Math.exp(growth) * (0.985 + 0.015 * employed);
      profits[index] = environment.capitalReturn * agent.capital * agent.occupation.exposure * Math.min(effectiveAI, 1.5);
      taxes[index] = policy.capitalDividend * profits[index];
      return { ...agent, skill, burden, adoption, effectiveAI, growth, employed, labor };
    });
    const taxPool = taxes.reduce((sum, value) => sum + value, 0);
    const profitPool = profits.reduce((sum, value) => sum + value, 0);
    const weights = next.map((agent) => 1.05 - agent.resource);
    const weightTotal = weights.reduce((sum, value) => sum + value, 0);
    agents = next.map((agent, index) => {
      const dividend = policy.capitalDividend ? taxPool * weights[index] / weightTotal : 0;
      const workerGrant = policy.workerOwnership * profitPool * weights[index] / weightTotal;
      const capital = Math.max(1e-6, 0.985 * agent.capital + 0.44 * (profits[index] - taxes[index]) + 0.02 * Math.max(agent.labor - agents[index].labor, 0) + workerGrant);
      const income = Math.max(1e-6, agent.labor + profits[index] - taxes[index] + dividend);
      return { ...agent, capital, income };
    });
    snapshots.push({ agents: cloneAgents(agents), metrics: calculateMetrics(agents, period) });
  }
  return { policy, environment, edges, snapshots, sourceLabel: profile ? `${profile.source} 집계 프로필` : "한국형 합성 기준집단" };
}

export function comparePolicies(environment: Environment, seed = 2026, profile?: PersonaProfile) {
  return (Object.keys(POLICIES) as PolicyKey[]).map((key) => runSimulation({
    policy: POLICIES[key], environment, seed, size: 360, periods: 15, profile,
  }));
}

export function incomeHistogram(agents: Agent[], bins = 12) {
  const values = agents.map((agent) => Math.log(Math.max(1e-6, agent.income)));
  const min = Math.min(...values); const max = Math.max(...values); const width = (max - min || 1) / bins;
  const counts = Array.from({ length: bins }, () => 0);
  values.forEach((value) => { counts[Math.min(bins - 1, Math.floor((value - min) / width))] += 1; });
  return counts.map((count, index) => ({ x: Math.exp(min + width * (index + 0.5)), count }));
}
