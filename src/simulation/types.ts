export type PolicyKey = "market" | "free" | "education" | "targeted" | "comprehensive" | "failed";

export type Policy = {
  key: PolicyKey;
  name: string;
  shortName: string;
  description: string;
  publicAccess: number;
  publicQuality: number;
  education: number;
  care: number;
  capitalDividend: number;
  workerOwnership: number;
  equalizingDesign: number;
  trust: number;
};

export type Environment = {
  premiumGap: number;
  reallocationSpeed: number;
  capitalReturn: number;
  feedback: number;
  networkSpillover: number;
  juniorDisplacement: number;
  ruralPenalty: number;
};

export type Occupation = {
  id: string;
  label: string;
  exposure: number;
  complementarity: number;
  baseIncome: number;
};

export type Agent = {
  id: number;
  age: number;
  female: boolean;
  region: string;
  rural: boolean;
  education: number;
  occupation: Occupation;
  resource: number;
  skill: number;
  capital: number;
  labor: number;
  income: number;
  initialIncome: number;
  flexibility: number;
  burden: number;
  vulnerable: boolean;
  premium: boolean;
  trust: number;
  employed: number;
  adoption: number;
  effectiveAI: number;
  growth: number;
};

export type Edge = { source: number; target: number };

export type Metrics = {
  period: number;
  gini: number;
  wolfson: number;
  atkinson: number;
  middleShare: number;
  topBottomRatio: number;
  skillGap: number;
  capitalTop10: number;
  output: number;
  ede: number;
  adoption: number;
  vulnerableEmployment: number;
};

export type Snapshot = { agents: Agent[]; metrics: Metrics };

export type SimulationRun = {
  policy: Policy;
  environment: Environment;
  edges: Edge[];
  snapshots: Snapshot[];
  sourceLabel: string;
};

export type PersonaStratum = {
  count: number;
  ageGroup?: string;
  sex?: string;
  region?: string;
  education?: string;
  occupation?: string;
};

export type PersonaProfile = {
  schemaVersion: number;
  source: string;
  license?: string;
  sampleSize: number;
  strata: PersonaStratum[];
  limitations?: string[];
};
