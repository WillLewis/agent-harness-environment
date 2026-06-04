export type PolicyId = 'baseline' | 'guarded_recovery' | 'baseline_with_steering';

export type TraceAction =
  | 'PLAN'
  | 'READ_FILE'
  | 'SEARCH'
  | 'EDIT'
  | 'TERMINAL'
  | 'TEST'
  | 'RETRY'
  | 'ASK_USER'
  | 'BLOCKED_ACTION'
  | 'POLICY_DECISION'
  | 'FINAL';

export type TraceEvent = {
  id: string;
  step: number;
  actor: 'planner' | 'executor' | 'critic' | 'router' | 'human' | 'judge' | 'subagent';
  action: TraceAction;
  title: string;
  summary: string;
  file?: string;
  command?: string;
  exitCode?: number;
  terminalOutput?: string;
  diff?: string;
  label?: string;
  raw?: Record<string, unknown>;
};

export type EvalMetrics = {
  taskSuccess: number;
  recoveryScore: number;
  loopScore: number;
  hallucinatedFiles: number;
  unsafeAttempts: number;
  humanInterventions: number;
  toolCalls: number;
  costCents: number;
};

export type PolicyRun = {
  id: PolicyId;
  name: string;
  description: string;
  verdict: 'accepted' | 'rejected' | 'assisted';
  primaryReason: string;
  events: TraceEvent[];
  metrics: EvalMetrics;
  judgeNotes: string[];
};

export const demoTask = {
  id: 'bugfix_date_parser_001',
  label: 'BUGFIX',
  title: 'timezone parser regression',
  issue: 'Date parser fails when timezone offset includes a colon.',
  successCommand: 'npm test -- dateParser',
  failureModes: ['premature_edit', 'ignored_test_output', 'loop_detected']
};

export const policyRuns: Record<PolicyId, PolicyRun> = {
  baseline: {
    id: 'baseline',
    name: 'Baseline',
    description: 'Minimal harness constraints. Good for exposing raw failure modes.',
    verdict: 'rejected',
    primaryReason: 'Loop detected: repeated failed command without new information.',
    metrics: {
      taskSuccess: 0,
      recoveryScore: 0.18,
      loopScore: 0.91,
      hallucinatedFiles: 0,
      unsafeAttempts: 0,
      humanInterventions: 0,
      toolCalls: 8,
      costCents: 8
    },
    judgeNotes: [
      'Agent edited before reading the failing assertion.',
      'Same failed command was repeated without new evidence.',
      'Final patch was plausible but did not pass target tests.'
    ],
    events: [
      { id: 'b1', step: 1, actor: 'planner', action: 'PLAN', title: 'Plan', summary: 'Inspect parser, patch likely offset handling, run dateParser tests.' },
      { id: 'b2', step: 2, actor: 'executor', action: 'READ_FILE', title: 'Read source', summary: 'Found parser delegates directly to Date constructor after light cleanup.', file: 'src/dateParser.ts' },
      { id: 'b3', step: 3, actor: 'executor', action: 'EDIT', title: 'Premature edit', summary: 'Replaced colon characters globally before reading the failing test.', file: 'src/dateParser.ts', label: 'premature_edit', diff: '- return new Date(input)\n+ return new Date(input.replace(/:/g, ""))' },
      { id: 'b4', step: 4, actor: 'executor', action: 'TEST', title: 'Target test failed', summary: 'Offset +05:30 still returns Invalid Date.', command: 'npm test -- dateParser', exitCode: 1, label: 'ignored_test_output', terminalOutput: 'FAIL tests/dateParser.test.ts\nExpected: 2026-06-03T18:30:00.000Z\nReceived: Invalid Date' },
      { id: 'b5', step: 5, actor: 'executor', action: 'RETRY', title: 'Retry without evidence', summary: 'The same command was retried before reading the assertion.', command: 'npm test -- dateParser', exitCode: 1, label: 'ignored_test_output' },
      { id: 'b6', step: 6, actor: 'executor', action: 'TEST', title: 'Loop detected', summary: 'The test failed again with the same assertion.', command: 'npm test -- dateParser', exitCode: 1, label: 'loop_detected', terminalOutput: 'FAIL tests/dateParser.test.ts\nExpected offset +05:30 to parse correctly.' },
      { id: 'b7', step: 7, actor: 'critic', action: 'BLOCKED_ACTION', title: 'Judge blocks run', summary: 'Repeated failed command without new information.', label: 'loop_detected' },
      { id: 'b8', step: 8, actor: 'judge', action: 'FINAL', title: 'Rejected', summary: 'Target test failed and loop was detected.' }
    ]
  },
  guarded_recovery: {
    id: 'guarded_recovery',
    name: 'Guarded recovery',
    description: 'Adds retry limits, loop breakers, unsafe-command blocking, and failure-output inspection.',
    verdict: 'accepted',
    primaryReason: 'Target tests and regression suite passed after evidence-driven recovery.',
    metrics: {
      taskSuccess: 1,
      recoveryScore: 0.86,
      loopScore: 0.02,
      hallucinatedFiles: 0,
      unsafeAttempts: 0,
      humanInterventions: 0,
      toolCalls: 10,
      costCents: 6
    },
    judgeNotes: [
      'Agent read the failing test before editing.',
      'After a failed test, the harness forced evidence gathering before retry.',
      'Final diff touched the expected file and passed regression checks.'
    ],
    events: [
      { id: 'g1', step: 1, actor: 'router', action: 'POLICY_DECISION', title: 'Policy selected', summary: 'Selected guarded_recovery for failed-test recovery risk.' },
      { id: 'g2', step: 2, actor: 'planner', action: 'PLAN', title: 'Evidence-first plan', summary: 'Inspect failing test, inspect parser, patch narrowly, run target and regression tests.' },
      { id: 'g3', step: 3, actor: 'executor', action: 'READ_FILE', title: 'Read failing test', summary: 'The test expects timezone offset +05:30 to parse correctly.', file: 'tests/dateParser.test.ts' },
      { id: 'g4', step: 4, actor: 'executor', action: 'READ_FILE', title: 'Read parser', summary: 'Parser strips punctuation too broadly before delegating to Date.', file: 'src/dateParser.ts' },
      { id: 'g5', step: 5, actor: 'executor', action: 'EDIT', title: 'Narrow patch', summary: 'Added timezone-offset normalizer without changing time separators.', file: 'src/dateParser.ts', diff: '+ const normalized = normalizeTimezoneOffset(input)\n+ return new Date(normalized)' },
      { id: 'g6', step: 6, actor: 'executor', action: 'TEST', title: 'Target test failed once', summary: 'Negative offset assertion failed; harness requires inspecting output before retry.', command: 'npm test -- dateParser', exitCode: 1, label: 'failed_recovery_guard_triggered', terminalOutput: 'FAIL tests/dateParser.test.ts\nExpected offset -04:00 to parse correctly.\nHarness: inspect failing assertion before retry.' },
      { id: 'g7', step: 7, actor: 'critic', action: 'READ_FILE', title: 'Inspect failure evidence', summary: 'Negative offsets require sign-preserving normalization.', file: 'tests/dateParser.test.ts' },
      { id: 'g8', step: 8, actor: 'executor', action: 'EDIT', title: 'Patch recovery', summary: 'Adjusted normalizer to preserve plus/minus sign and remove only offset colon.', file: 'src/dateParser.ts', diff: "+ return input.replace(/([+-]\\d{2}):(\\d{2})$/, '$1$2')" },
      { id: 'g9', step: 9, actor: 'executor', action: 'TEST', title: 'Tests passed', summary: 'Target tests and full regression suite passed.', command: 'npm test -- dateParser && npm test', exitCode: 0, terminalOutput: 'PASS tests/dateParser.test.ts\nPASS tests/regression.test.ts' },
      { id: 'g10', step: 10, actor: 'judge', action: 'FINAL', title: 'Accepted', summary: 'Target tests passed, regression free, no loop, expected file touched.' }
    ]
  },
  baseline_with_steering: {
    id: 'baseline_with_steering',
    name: 'Baseline + steering',
    description: 'Baseline run rescued by one human intervention at the loop-risk moment.',
    verdict: 'assisted',
    primaryReason: 'Accepted with one human intervention that forced evidence gathering.',
    metrics: {
      taskSuccess: 1,
      recoveryScore: 0.71,
      loopScore: 0.08,
      hallucinatedFiles: 0,
      unsafeAttempts: 0,
      humanInterventions: 1,
      toolCalls: 11,
      costCents: 7
    },
    judgeNotes: [
      'Human steering changed outcome at the repeated-test moment.',
      'This is assisted success, not autonomous success.',
      'The harness should learn to catch this pattern automatically.'
    ],
    events: [
      { id: 's1', step: 1, actor: 'planner', action: 'PLAN', title: 'Plan', summary: 'Inspect parser, patch likely offset handling, run dateParser tests.' },
      { id: 's2', step: 2, actor: 'executor', action: 'READ_FILE', title: 'Read source', summary: 'Found parser delegates directly to Date constructor after light cleanup.', file: 'src/dateParser.ts' },
      { id: 's3', step: 3, actor: 'executor', action: 'EDIT', title: 'Premature edit', summary: 'Replaced colon characters globally before reading the failing test.', file: 'src/dateParser.ts', label: 'premature_edit', diff: '- return new Date(input)\n+ return new Date(input.replace(/:/g, ""))' },
      { id: 's4', step: 4, actor: 'executor', action: 'TEST', title: 'Target test failed', summary: 'Offset +05:30 still returns Invalid Date.', command: 'npm test -- dateParser', exitCode: 1, terminalOutput: 'FAIL tests/dateParser.test.ts\nExpected offset +05:30 to parse correctly.' },
      { id: 's5', step: 5, actor: 'human', action: 'ASK_USER', title: 'Steering applied', summary: 'Stop rerunning tests. Inspect the failing assertion and parser implementation.' },
      { id: 's6', step: 6, actor: 'executor', action: 'READ_FILE', title: 'Read failing test', summary: 'The test expects timezone offset +05:30 to parse correctly.', file: 'tests/dateParser.test.ts' },
      { id: 's7', step: 7, actor: 'executor', action: 'EDIT', title: 'Corrected patch', summary: 'Added sign-preserving offset normalizer.', file: 'src/dateParser.ts', diff: "+ return input.replace(/([+-]\\d{2}):(\\d{2})$/, '$1$2')" },
      { id: 's8', step: 8, actor: 'executor', action: 'TEST', title: 'Tests passed', summary: 'Target tests and regression suite passed.', command: 'npm test -- dateParser && npm test', exitCode: 0, terminalOutput: 'PASS tests/dateParser.test.ts\nPASS tests/regression.test.ts' },
      { id: 's9', step: 9, actor: 'judge', action: 'FINAL', title: 'Assisted accepted', summary: 'Accepted with one human intervention.' }
    ]
  }
};

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
