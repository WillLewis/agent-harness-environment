export type {
  EvalMetrics,
  EvidenceTab,
  PolicyId,
  PolicyRun,
  TraceAction,
  TraceEvent
} from './cockpitTypes';
export { evidenceTabs } from './cockpitTypes';
export { demoTask, policyRuns } from './cockpitFixtures';
export { policyComparison, failureClusters, getFailureCluster, policyDisplayName } from './evalFixtures';

export const routerDecision = {
  taskFeatures: {
    task_type: 'bugfix',
    risk_level: 'medium',
    expected_files: 'one',
    recent_failure_pattern: 'ignored_test_output'
  },
  selectedPolicy: 'guarded_recovery',
  why: 'Highest expected reward for bugfix tasks with failed-test recovery risk.',
  expectedRewards: [
    ['baseline', 1.9],
    ['test_first', 3.8],
    ['context_first', 3.2],
    ['guarded_recovery', 4.6],
    ['high_reasoning_on_failure', 4.1]
  ] as const
};
