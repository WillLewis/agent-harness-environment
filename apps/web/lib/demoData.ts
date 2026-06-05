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

export const policyComparison = [
  { policy: 'Baseline', success: '56%', recovery: '31%', loop: '14%', hallucinatedFiles: '18%', unsafeAttempts: '3%', humanInterventions: '2.1', cost: '$' },
  { policy: 'Test-first', success: '72%', recovery: '58%', loop: '8%', hallucinatedFiles: '10%', unsafeAttempts: '2%', humanInterventions: '1.4', cost: '$$' },
  { policy: 'Guarded recovery', success: '84%', recovery: '76%', loop: '3%', hallucinatedFiles: '4%', unsafeAttempts: '0%', humanInterventions: '0.8', cost: '$$' },
  { policy: 'RL-lite router', success: '88%', recovery: '80%', loop: '2%', hallucinatedFiles: '4%', unsafeAttempts: '0%', humanInterventions: '0.7', cost: '$' }
];

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
