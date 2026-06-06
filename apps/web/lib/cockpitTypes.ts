export type TaskId =
  | 'bugfix_date_parser_001'
  | 'adversarial_env_001'
  | 'multi_agent_contract_001';

export type TaskType = 'bugfix' | 'adversarial' | 'multi_agent';

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
  harnessNote?: string;
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

export type CockpitTask = {
  id: TaskId;
  type: TaskType;
  typeLabel: string;
  label: string;
  repo: string;
  title: string;
  issue: string;
  successCommand: string;
  tags: string[];
  failureModes: string[];
  expectedFiles: string[];
  knownFiles: string[];
  defaultPolicyId: PolicyId;
  policyOrder: PolicyId[];
  policies: Partial<Record<PolicyId, PolicyRun>>;
};

export const evidenceTabs = ['files', 'terminal', 'diff', 'judge', 'raw'] as const;
export type EvidenceTab = (typeof evidenceTabs)[number];
