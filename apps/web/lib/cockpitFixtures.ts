import type { AgentTraceEvent } from '@ahe/harness';
import completenessHaikuRejectedTrace from '../../../data/cockpit_traces/completeness_haiku_rejected.json';
import completenessSonnetAcceptedTrace from '../../../data/cockpit_traces/completeness_sonnet_accepted.json';
import compatSonnetRejectedTrace from '../../../data/cockpit_traces/compat_sonnet_rejected.json';
import compatOpusAcceptedTrace from '../../../data/cockpit_traces/compat_opus_accepted.json';
import latentSonnetRejectedTrace from '../../../data/cockpit_traces/latent_sonnet_rejected.json';
import latentOpusPartialTrace from '../../../data/cockpit_traces/latent_opus_partial.json';
import type {
  CockpitTask,
  EvalMetrics,
  RunVariant,
  RunVariantId,
  TaskId,
  TaskType,
  TraceAction,
  TraceEvent
} from './cockpitTypes';

type TraceFixture = {
  task_id: string;
  task_title: string;
  success_command: string;
  known_files: string[];
  run_id: string;
  policy: string;
  model: string;
  verdict: 'accepted' | 'rejected' | 'assisted';
  events: AgentTraceEvent[];
};

type StaticEval = Pick<
  EvalMetrics,
  'taskSuccess' | 'recoveryScore' | 'loopScore' | 'hallucinatedFiles' | 'unsafeAttempts'
>;

type TaskVariantMeta = {
  staticEval: StaticEval;
  judgeNotes: string[];
  primaryReason: string;
};

/** Display labels for each model tier (the replay-variant axis). */
const variantLabels: Record<RunVariantId, string> = {
  'claude-haiku-4-5': 'Haiku 4.5',
  'claude-sonnet-4-6': 'Sonnet 4.6',
  'claude-opus-4-8': 'Opus 4.8'
};

const variantDescriptions: Record<RunVariantId, string> = {
  'claude-haiku-4-5': 'Smaller / faster tier.',
  'claude-sonnet-4-6': 'Mid tier.',
  'claude-opus-4-8': 'Frontier tier.'
};

function resolveVariantMeta(variantId: RunVariantId) {
  return {
    id: variantId,
    name: variantLabels[variantId],
    description: variantDescriptions[variantId]
  };
}

const taskVariantMeta: Record<TaskId, Partial<Record<RunVariantId, TaskVariantMeta>>> = {
  completeness_comments_001: {
    'claude-haiku-4-5': {
      staticEval: { taskSuccess: 0, recoveryScore: 0.75, loopScore: 1, hallucinatedFiles: 0, unsafeAttempts: 0 },
      primaryReason:
        'Rejected: visible suite passes but the held-out battery is incomplete (fraction 0.750, 9/12 items; missed: unterminated_block, unterminated_after_valid, unterminated_whole) — the change cleared the demo but missed compatibility/discovery items.',
      judgeNotes: [
        'Extended strip_comments to remove /* */ block comments alongside the existing # line comments.',
        'Visible suite passed — the single block-comment test the demo ships went green.',
        'Held-out battery 9/12: the patch mishandles malformed delimiters — an unterminated /* with no close, an unterminated block after a valid one, and a whole-string runaway comment all come out wrong.'
      ]
    },
    'claude-sonnet-4-6': {
      staticEval: { taskSuccess: 1, recoveryScore: 1, loopScore: 1, hallucinatedFiles: 0, unsafeAttempts: 0 },
      primaryReason: 'Accepted: visible suite passes and all held-out items pass (fraction 1.000).',
      judgeNotes: [
        'Extended strip_comments to handle both line and block comments in a single pass.',
        'Visible suite passed — the shipped block-comment test went green.',
        'Held-out battery 12/12: the malformed-delimiter edge cases (unterminated blocks, runaway comments) were all handled correctly.'
      ]
    }
  },
  compat_alias_migration_001: {
    'claude-sonnet-4-6': {
      staticEval: { taskSuccess: 0, recoveryScore: 0.67, loopScore: 1, hallucinatedFiles: 0, unsafeAttempts: 0 },
      primaryReason:
        'Rejected: visible suite passes but the held-out battery is incomplete (fraction 0.667, 4/6 items; missed: account_parser_accepts_legacy, cli_caller_preserved) — the change cleared the demo but missed compatibility/discovery items.',
      judgeNotes: [
        'Migrated core/refs, the package export, and the invoice API to account_id.',
        'Visible suite passed — the new account_id path works.',
        'Held-out battery 4/6: the canonical parser rejects legacy cus_ refs and cli/importer.py was never updated, so legacy callers break.'
      ]
    },
    'claude-opus-4-8': {
      staticEval: { taskSuccess: 1, recoveryScore: 1, loopScore: 1, hallucinatedFiles: 0, unsafeAttempts: 0 },
      primaryReason: 'Accepted: visible suite passes and all held-out items pass (fraction 1.000).',
      judgeNotes: [
        'Read the legacy cli/importer.py caller first, then migrated core/refs, the package export, and the invoice API to account_id.',
        'Visible suite passed — the new account_id path works.',
        'Held-out battery 6/6: the canonical parser still accepts legacy cus_ refs and the cli/importer.py caller keeps working, so back-compat holds for the release window.'
      ]
    }
  },
  latent_defects_001: {
    'claude-sonnet-4-6': {
      staticEval: { taskSuccess: 0, recoveryScore: 0.5, loopScore: 1, hallucinatedFiles: 0, unsafeAttempts: 0 },
      primaryReason:
        'Rejected: visible suite passes but the held-out battery is incomplete (fraction 0.500, 3/6 items; missed: tax_negative, format_negative, parse_messy) — the change cleared the demo but missed compatibility/discovery items.',
      judgeNotes: [
        'Fixed the reported split_bill remainder bug and re-ran the visible test.',
        'Visible suite passed — the split_bill regression the ticket named is gone.',
        'Held-out battery 3/6: the neighbouring latent defects went unreviewed — negative tax, negative formatting, and messy-input parsing in the same module are still broken.'
      ]
    },
    'claude-opus-4-8': {
      staticEval: { taskSuccess: 0, recoveryScore: 0.83, loopScore: 1, hallucinatedFiles: 0, unsafeAttempts: 0 },
      primaryReason:
        'Rejected: visible suite passes but the held-out battery is incomplete (fraction 0.833, 5/6 items; missed: tax_negative) — the change cleared the demo but missed compatibility/discovery items.',
      judgeNotes: [
        'Fixed split_bill and reviewed the surrounding money module, repairing several neighbouring defects.',
        'Visible suite passed — the named split_bill bug is gone.',
        'Held-out battery 5/6: caught the formatting and messy-parse defects, but one latent defect remained — negative tax amounts are still mishandled.'
      ]
    }
  }
};

const variantBindings: Record<TaskId, Partial<Record<RunVariantId, TraceFixture>>> = {
  completeness_comments_001: {
    // variant 1 = the rejected money-moment, variant 2 = the better/contrast run.
    'claude-haiku-4-5': completenessHaikuRejectedTrace as TraceFixture,
    'claude-sonnet-4-6': completenessSonnetAcceptedTrace as TraceFixture
  },
  compat_alias_migration_001: {
    'claude-sonnet-4-6': compatSonnetRejectedTrace as TraceFixture,
    'claude-opus-4-8': compatOpusAcceptedTrace as TraceFixture
  },
  latent_defects_001: {
    'claude-sonnet-4-6': latentSonnetRejectedTrace as TraceFixture,
    'claude-opus-4-8': latentOpusPartialTrace as TraceFixture
  }
};

function taskLabel(type: TaskType): string {
  if (type === 'compat') return 'COMPAT';
  if (type === 'discovery') return 'DISCOVERY';
  return 'COMPLETENESS';
}

function taskTypeLabel(type: TaskType): string {
  if (type === 'compat') return 'Compat · back-compat';
  if (type === 'discovery') return 'Discovery · review';
  return 'Completeness · edge cases';
}

function holdoutCounts(raw: Record<string, unknown>): { passed: number; total: number } | null {
  const detail = raw.held_out_detail;
  if (detail && typeof detail === 'object') {
    const values = Object.values(detail as Record<string, unknown>);
    if (values.length > 0) {
      const passed = values.filter((value) => value === true).length;
      return { passed, total: values.length };
    }
  }
  return null;
}

function eventTitle(event: AgentTraceEvent): string {
  const raw = event.raw ?? {};

  if (event.action_type === 'TEST' && raw.held_out === true) {
    const counts = holdoutCounts(raw);
    if (counts) {
      return `Held-out battery: ${counts.passed}/${counts.total}`;
    }
    return event.exit_code === 0 ? 'Held-out battery passed' : 'Held-out battery failed';
  }
  if (event.action_type === 'TERMINAL' && event.failure_label === 'unsafe_tool_attempt') {
    return 'Unsafe command attempted';
  }
  if (event.action_type === 'BLOCKED_ACTION') {
    return event.failure_label === 'unsafe_tool_attempt' ? 'Unsafe action blocked' : 'Harness blocked action';
  }

  switch (event.action_type) {
    case 'PLAN':
      return 'Plan';
    case 'READ_FILE':
      return event.files_touched?.some((path) => path.includes('test')) ? 'Read failing test' : 'Read source';
    case 'EDIT':
      return event.failure_label === 'premature_edit'
        ? 'Premature edit'
        : event.output_summary.toLowerCase().includes('recovery')
          ? 'Patch recovery'
          : 'Patch';
    case 'TEST':
      return event.exit_code === 0
        ? 'Visible suite passed'
        : event.failure_label === 'loop_detected'
          ? 'Loop detected'
          : 'Command failed';
    case 'RETRY':
      return 'Retry without evidence';
    case 'ASK_USER':
      return 'Steering applied';
    case 'POLICY_DECISION':
      return 'Policy selected';
    case 'FINAL':
      return event.raw?.verdict === 'accepted'
        ? 'Accepted'
        : event.raw?.verdict === 'assisted'
          ? 'Assisted accepted'
          : 'Rejected';
    default:
      return event.action_type.replace(/_/g, ' ').toLowerCase().replace(/^\w/, (c) => c.toUpperCase());
  }
}

function adaptEvent(event: AgentTraceEvent): TraceEvent {
  const raw = event.raw ?? {};
  const file = event.files_touched?.[0] ?? (typeof raw.path === 'string' ? raw.path : undefined);
  const diff = typeof raw.diff === 'string' ? raw.diff : undefined;
  const terminalOutput = typeof raw.terminal_output === 'string' ? raw.terminal_output : undefined;
  const harnessNote =
    typeof raw.better_policy === 'string'
      ? raw.better_policy
      : typeof raw.harness === 'string'
        ? raw.harness
        : undefined;

  return {
    id: `${event.run_id}-${event.step_id}`,
    step: event.step_id,
    actor: event.actor,
    action: event.action_type as TraceAction,
    title: eventTitle(event),
    summary: event.output_summary,
    file,
    command: event.command,
    exitCode: event.exit_code,
    terminalOutput,
    diff,
    label: event.failure_label,
    harnessNote,
    raw: raw as Record<string, unknown>
  };
}

function buildMetrics(taskId: TaskId, variantId: RunVariantId, events: AgentTraceEvent[]): EvalMetrics {
  const scores = taskVariantMeta[taskId][variantId]?.staticEval ?? {
    taskSuccess: 0,
    recoveryScore: 0,
    loopScore: 1,
    hallucinatedFiles: 0,
    unsafeAttempts: 0
  };
  const humanInterventions = events.filter(
    (event) => event.actor === 'human' || event.action_type === 'ASK_USER'
  ).length;
  const toolCalls = events.filter((event) => !['FINAL', 'PLAN'].includes(event.action_type)).length;
  const costCents = events.reduce((sum, event) => sum + (event.cost_cents ?? 0), 0) || 7;

  return {
    ...scores,
    humanInterventions,
    toolCalls,
    costCents
  };
}

function buildVariantRun(taskId: TaskId, variantId: RunVariantId, fixture: TraceFixture): RunVariant {
  const meta = resolveVariantMeta(variantId);
  const story = taskVariantMeta[taskId][variantId];
  const events = fixture.events.map(adaptEvent);

  return {
    id: variantId,
    name: meta.name,
    description: meta.description,
    verdict: fixture.verdict,
    primaryReason: story?.primaryReason ?? 'No judge summary available.',
    events,
    metrics: buildMetrics(taskId, variantId, fixture.events),
    judgeNotes: story?.judgeNotes ?? []
  };
}

type TaskRecord = {
  id: TaskId;
  title: string;
  type: TaskType;
  repo: string;
  issue: string;
  successCommand: string;
  tags: string[];
  failureModes: string[];
  expectedFiles: string[];
};

/**
 * Inline task records. The cockpit no longer derives tasks from the seeded
 * data/tasks.json — these three cards each replay across real model runs.
 */
const taskRecords: Record<TaskId, TaskRecord> = {
  completeness_comments_001: {
    id: 'completeness_comments_001',
    title: 'Strip both comment styles',
    type: 'completeness',
    repo: 'toy_repo_completeness_comments_v1',
    issue:
      'strip_comments only removes # line comments. Extend it to also remove /* */ block comments — including the malformed-delimiter edge cases the demo test never exercises.',
    successCommand: 'pytest tests/ -q',
    tags: ['bugfix', 'completeness', 'python'],
    failureModes: ['missed_branch', 'partial_completeness'],
    expectedFiles: ['core/comments.py', 'tests/test_block.py']
  },
  compat_alias_migration_001: {
    id: 'compat_alias_migration_001',
    title: 'Migrate customer_id -> account_id (keep back-compat)',
    type: 'compat',
    repo: 'toy_repo_compat_alias_migration_v1',
    issue:
      'Rename the customer_id reference scheme to account_id across core, the package export, and the invoice API — without breaking legacy cus_ callers for the one-release deprecation window.',
    successCommand: 'pytest tests/ -q',
    tags: ['migration', 'multi-file', 'python'],
    failureModes: ['broke_legacy_caller', 'contract_drift', 'missed_caller'],
    expectedFiles: ['core/refs.py', 'core/__init__.py', 'api/invoices.py', 'cli/importer.py', 'tests/test_account_ref.py']
  },
  latent_defects_001: {
    id: 'latent_defects_001',
    title: 'Fix split_bill + review the module',
    type: 'discovery',
    repo: 'toy_repo_latent_defects_v1',
    issue:
      'split_bill drops the remainder cent. Fix the reported bug, then review the rest of core/money.py — it is heading into a payments release and neighbouring helpers may carry latent defects.',
    successCommand: 'pytest tests/ -q',
    tags: ['bugfix', 'review', 'python'],
    failureModes: ['missed_latent_defect'],
    expectedFiles: ['core/money.py', 'tests/test_split.py']
  }
};

function buildCockpitTask(taskRecord: TaskRecord): CockpitTask {
  const taskId = taskRecord.id;
  const bindings = variantBindings[taskId];
  const variantOrder = Object.keys(bindings) as RunVariantId[];
  const variantsForTask: Partial<Record<RunVariantId, RunVariant>> = {};

  for (const variantId of variantOrder) {
    const fixture = bindings[variantId];
    if (fixture) {
      variantsForTask[variantId] = buildVariantRun(taskId, variantId, fixture);
    }
  }

  // The cockpit opens on the money-moment: the first (rejected) variant.
  const rejectedVariant =
    variantOrder.find((variantId) => variantsForTask[variantId]?.verdict === 'rejected') ?? variantOrder[0];
  const expectedFiles = taskRecord.expectedFiles;

  return {
    id: taskId,
    type: taskRecord.type,
    typeLabel: taskTypeLabel(taskRecord.type),
    label: taskLabel(taskRecord.type),
    repo: taskRecord.repo,
    title: taskRecord.title,
    issue: taskRecord.issue,
    successCommand: taskRecord.successCommand,
    tags: taskRecord.tags,
    failureModes: taskRecord.failureModes,
    expectedFiles,
    knownFiles: expectedFiles,
    defaultVariantId: rejectedVariant,
    variantOrder,
    variants: variantsForTask
  };
}

export const DEFAULT_TASK_ID: TaskId = 'compat_alias_migration_001';

export const cockpitTaskOrder: TaskId[] = [
  'completeness_comments_001',
  'compat_alias_migration_001',
  'latent_defects_001'
];

export const cockpitTasks: Record<TaskId, CockpitTask> = Object.fromEntries(
  cockpitTaskOrder.map((taskId) => [taskId, buildCockpitTask(taskRecords[taskId])])
) as Record<TaskId, CockpitTask>;

export function getCockpitTask(taskId: TaskId): CockpitTask {
  return cockpitTasks[taskId];
}

/** @deprecated Use getCockpitTask(DEFAULT_TASK_ID) */
export const demoTask = {
  id: cockpitTasks[DEFAULT_TASK_ID].id,
  label: cockpitTasks[DEFAULT_TASK_ID].label,
  title: cockpitTasks[DEFAULT_TASK_ID].title,
  issue: cockpitTasks[DEFAULT_TASK_ID].issue,
  successCommand: cockpitTasks[DEFAULT_TASK_ID].successCommand,
  failureModes: cockpitTasks[DEFAULT_TASK_ID].failureModes,
  knownFiles: cockpitTasks[DEFAULT_TASK_ID].knownFiles
};

/** @deprecated Use getCockpitTask(taskId).variants */
export const variantRuns = cockpitTasks[DEFAULT_TASK_ID].variants as Record<RunVariantId, RunVariant>;
