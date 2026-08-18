import assert from "node:assert/strict";
import test from "node:test";
import { DEFAULT_ENVIRONMENT, gini, POLICIES, runSimulation, wolfson } from "./model";

test("the browser model is deterministic for a fixed seed", () => {
  const first = runSimulation({ policy: POLICIES.targeted, seed: 11, size: 120, periods: 4 });
  const second = runSimulation({ policy: POLICIES.targeted, seed: 11, size: 120, periods: 4 });
  assert.deepEqual(first.snapshots.map((item) => item.metrics), second.snapshots.map((item) => item.metrics));
});

test("equal incomes produce zero inequality", () => {
  assert.ok(Math.abs(gini([2, 2, 2, 2])) < 1e-12);
  assert.ok(Math.abs(wolfson([2, 2, 2, 2])) < 1e-12);
});

test("all headline metrics stay finite", () => {
  const run = runSimulation({ policy: POLICIES.education, environment: DEFAULT_ENVIRONMENT, size: 160, periods: 5 });
  for (const snapshot of run.snapshots) {
    for (const value of Object.values(snapshot.metrics)) assert.ok(Number.isFinite(value));
  }
});

test("education closes more of the skill gap than access alone", () => {
  const free = runSimulation({ policy: POLICIES.free, size: 220, periods: 8 });
  const education = runSimulation({ policy: POLICIES.education, size: 220, periods: 8 });
  assert.ok(education.snapshots.at(-1)!.metrics.skillGap < free.snapshots.at(-1)!.metrics.skillGap);
});
