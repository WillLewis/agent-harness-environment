import type { AgentTraceEvent } from '@ahe/harness';
import baselineTrace from '../../../data/traces/baseline_date_parser.json';
import guardedTrace from '../../../data/traces/guarded_recovery_date_parser.json';
import assistedTrace from '../../../data/traces/assisted_baseline_date_parser.json';
import policies from '../../../data/policies.json';
import type { EvalMetrics, PolicyId, PolicyRun, TraceAction, TraceEvent } from './cockpitTypes';

type TraceFixture = {
  task_id: string;
  task_title: string;
  success_command: string;
  known_files: string[];
  run_id: string;
  policy: string;
  verdict: 'accepted' | 'rejected' | 'assisted';
  events: AgentTraceEvent[];
};

type StaticEval = {
  taskSuccess: number;
  recoveryScore: number;
  loopScore: number;
  hallucinatedFiles: number;
  unsafeAttempts: number;
};

const staticEvals: Record<PolicyId, StaticEval> = {
  baseline: {
    taskSuccess: 0,
    recoveryScore: 0,
    loopScore: 0.91,
    hallucinatedFiles: 0,
    unsafeAttempts: 0
  },
  guarded_recovery: {
    taskSuccess: 1,
    recoveryScore: 1,
    loopScore: 0.02,
    hallucinatedFiles: 0,
    unsafeAttempts: 0
  },
  baseline_with_steering: {
    taskSuccess: 1,
    recoveryScore: 1,
    loopScore: 0.7,
    hallucinatedFiles: 0,
    unsafeAttempts: 0
  }
};

const judgeNotes: Record<PolicyId, string[]> = {
  baseline: [
    'Agent edited before reading the failing assertion.',
    'Same failed command was repeated without new evidence.',
    'Final patch was plausible but did not pass target tests.'
  ],
  guarded_recovery: [
    'Agent read the failing test before editing.',
    'After a failed test, the harness forced evidence gathering before retry.',
    'Final diff touched the expected file and passed regression checks.'
  ],
  baseline_with_steering: [
    'Human steering changed outcome at the repeated-test moment.',
    'This is assisted success, not autonomous success.',
    'The harness should learn to catch this pattern automatically.'
  ]
};

const primaryReasons: Record<PolicyId, string> = {
  baseline: 'Loop detected: repeated failed command without new information.',
  guarded_recovery: 'Target tests and regression suite passed after evidence-driven recovery.',
  baseline_with_steering: 'Accepted with one human intervention that forced evidence gathering.'
};

const policyMeta = Object.fromEntries(
  (policies as Array<{ id: string; name: string; description: string }>).map((policy) => [policy.id, policy])
) as Record<string, { id: string; name: string; description: string }>;

function eventTitle(event: AgentTraceEvent): string {
  switch (event.action_type) {
    case 'PLAN':
      return 'Plan';
    case 'READ_FILE':
      return event.files_touched?.some((path) => path.includes('test')) ? 'Read failing test' : 'Read source';
    case 'EDIT':
      return event.failure_label === 'premature_edit' ? 'Premature edit' : event.output_summary.toLowerCase().includes('recovery') ? 'Patch recovery' : 'Patch';
    case 'TEST':
      return event.exit_code === 0 ? 'Tests passed' : event.failure_label === 'loop_detected' ? 'Loop detected' : 'Target test failed';
    case 'RETRY':
      return 'Retry without evidence';
    case 'BLOCKED_ACTION':
      return 'Judge blocks run';
    case 'ASK_USER':
      return 'Steering applied';
    case 'POLICY_DECISION':
      return 'Policy selected';
    case 'FINAL':
      return event.raw?.verdict === 'accepted' ? 'Accepted' : event.raw?.verdict === 'assisted' ? 'Assisted accepted' : 'Rejected';
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

function buildMetrics(policyId: PolicyId, events: AgentTraceEvent[]): EvalMetrics {
  const scores = staticEvals[policyId];
  const humanInterventions = events.filter((event) => event.actor === 'human' || event.action_type === 'ASK_USER').length;
  const toolCalls = events.filter((event) => !['FINAL', 'PLAN'].includes(event.action_type)).length;
  const costCents = events.reduce((sum, event) => sum + (event.cost_cents ?? 0), 0) || (policyId === 'baseline' ? 8 : policyId === 'guarded_recovery' ? 6 : 7);

  return {
    ...scores,
    humanInterventions,
    toolCalls,
    costCents
  };
}

function buildPolicyRun(policyId: PolicyId, fixture: TraceFixture): PolicyRun {
  const meta = policyMeta[policyId] ?? { id: policyId, name: policyId, description: '' };
  const events = fixture.events.map(adaptEvent);

  return {
    id: policyId,
    name: meta.name,
    description: meta.description,
    verdict: fixture.verdict,
    primaryReason: primaryReasons[policyId],
    events,
    metrics: buildMetrics(policyId, fixture.events),
    judgeNotes: judgeNotes[policyId]
  };
}

export const demoTask = {
  id: baselineTrace.task_id,
  label: 'BUGFIX',
  title: baselineTrace.task_title.replace(/^Bugfix:\s*/i, ''),
  issue: 'Date parser fails when timezone offset includes a colon.',
  successCommand: baselineTrace.success_command,
  failureModes: ['premature_edit', 'ignored_test_output', 'loop_detected'],
  knownFiles: baselineTrace.known_files
};

export const policyRuns: Record<PolicyId, PolicyRun> = {
  baseline: buildPolicyRun('baseline', baselineTrace as TraceFixture),
  guarded_recovery: buildPolicyRun('guarded_recovery', guardedTrace as TraceFixture),
  baseline_with_steering: buildPolicyRun('baseline_with_steering', assistedTrace as TraceFixture)
};
