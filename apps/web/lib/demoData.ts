import routerDecisionsJson from '../../../data/router_decisions.json';

export type {
  CockpitTask,
  EvalMetrics,
  EvidenceTab,
  PolicyId,
  PolicyRun,
  TaskId,
  TraceAction,
  TraceEvent
} from './cockpitTypes';
export { evidenceTabs } from './cockpitTypes';
export {
  cockpitTaskOrder,
  cockpitTasks,
  DEFAULT_TASK_ID,
  demoTask,
  getCockpitTask,
  policyRuns
} from './cockpitFixtures';
export { policyComparison, failureClusters, getFailureCluster, policyDisplayName } from './evalFixtures';

type RouterFixture = {
  taskFeatures: Record<string, string>;
  selectedPolicy: string;
  why: string;
  expectedRewards: Record<string, number>;
  policyStats?: Record<
    string,
    {
      count: number;
      mean_reward: number;
      last_reward: number | null;
      total_reward: number;
    }
  >;
};

const routerDecisionMap = routerDecisionsJson as Record<string, RouterFixture>;

function normalizeRouterDecision(taskId: string, decision: RouterFixture) {
  return {
    taskId,
    taskFeatures: decision.taskFeatures,
    selectedPolicy: decision.selectedPolicy,
    why: decision.why,
    expectedRewards: Object.entries(decision.expectedRewards),
    policyStats: decision.policyStats ?? {}
  };
}

export const routerDecisions = Object.entries(routerDecisionMap).map(([taskId, decision]) =>
  normalizeRouterDecision(taskId, decision)
);

export const routerDecision =
  routerDecisions.find((decision) => decision.taskId === 'bugfix_date_parser_001') ?? routerDecisions[0];
