export type TraceActor = 'planner' | 'executor' | 'critic' | 'router' | 'human' | 'judge' | 'subagent';

export type TraceActionType =
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

export type AgentTraceEvent = {
  run_id: string;
  task_id: string;
  step_id: number;
  timestamp: string;
  actor: TraceActor;
  action_type: TraceActionType;
  input_summary: string;
  output_summary: string;
  files_touched?: string[];
  command?: string;
  exit_code?: number;
  harness_policy: string;
  model?: string;
  tokens?: number;
  latency_ms?: number;
  cost_cents?: number;
  failure_label?: string;
  raw?: Record<string, unknown>;
};

export function createTraceEvent(event: Omit<AgentTraceEvent, 'timestamp'> & { timestamp?: string }): AgentTraceEvent {
  return {
    ...event,
    timestamp: event.timestamp ?? new Date().toISOString()
  };
}

export function validateTraceEvent(event: AgentTraceEvent): string[] {
  const errors: string[] = [];
  if (!event.run_id) errors.push('run_id is required');
  if (!event.task_id) errors.push('task_id is required');
  if (!Number.isInteger(event.step_id)) errors.push('step_id must be an integer');
  if (!event.timestamp) errors.push('timestamp is required');
  if (!event.actor) errors.push('actor is required');
  if (!event.action_type) errors.push('action_type is required');
  if (!event.input_summary) errors.push('input_summary is required');
  if (!event.output_summary) errors.push('output_summary is required');
  if (!event.harness_policy) errors.push('harness_policy is required');
  return errors;
}
