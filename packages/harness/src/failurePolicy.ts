import type { AgentTraceEvent } from './trace';

export function detectRepeatedCommand(events: AgentTraceEvent[], threshold = 2): boolean {
  const recentCommands = events
    .filter((event) => event.action_type === 'TEST' || event.action_type === 'TERMINAL' || event.action_type === 'RETRY')
    .map((event) => `${event.command ?? ''}:${event.exit_code ?? ''}`)
    .filter(Boolean);

  if (recentCommands.length < threshold) return false;
  const last = recentCommands.at(-1);
  return recentCommands.slice(-threshold).every((command) => command === last);
}

export function hasEvidenceAfterFailure(events: AgentTraceEvent[], failedStep: number): boolean {
  return events.some((event) => event.step_id > failedStep && ['READ_FILE', 'SEARCH', 'ASK_USER'].includes(event.action_type));
}

export function labelFailure(events: AgentTraceEvent[]): string | undefined {
  if (detectRepeatedCommand(events, 2)) return 'loop_detected';
  const hasPrematureEdit = events.some((event) => event.failure_label === 'premature_edit');
  if (hasPrematureEdit) return 'premature_edit';
  return undefined;
}
