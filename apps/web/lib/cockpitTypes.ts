export type TaskId =
  | 'completeness_comments_001'
  | 'compat_alias_migration_001'
  | 'latent_defects_001';

export type TaskType = 'completeness' | 'compat' | 'discovery';

/**
 * The replay axis is now the MODEL TIER, not a harness policy. Each card replays
 * across the real model runs that were captured for it; the variant id is the
 * model slug used in the trace.
 */
export type RunVariantId =
  | 'claude-haiku-4-5'
  | 'claude-sonnet-4-6'
  | 'claude-opus-4-8';

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

export type RunVariant = {
  id: RunVariantId;
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
  defaultVariantId: RunVariantId;
  variantOrder: RunVariantId[];
  variants: Partial<Record<RunVariantId, RunVariant>>;
};

export const evidenceTabs = ['files', 'terminal', 'diff', 'judge', 'raw'] as const;
export type EvidenceTab = (typeof evidenceTabs)[number];
