import type { EvidenceTab, TraceEvent } from './cockpitTypes';

export function tabForEvent(event: TraceEvent): EvidenceTab {
  if (event.action === 'EDIT') return 'diff';
  if (event.action === 'TEST' || event.action === 'RETRY' || event.action === 'TERMINAL') return 'terminal';
  if (event.action === 'READ_FILE' || event.action === 'SEARCH') return 'files';
  if (event.action === 'FINAL' || event.action === 'BLOCKED_ACTION' || event.action === 'ASK_USER' || event.action === 'POLICY_DECISION') {
    return 'judge';
  }
  return 'terminal';
}

export function defaultTabForPolicy(policyId: string): EvidenceTab {
  return policyId === 'guarded_recovery' ? 'judge' : 'terminal';
}

export function findEvent(events: TraceEvent[], step: number): TraceEvent {
  return events.find((event) => event.step === step) ?? events[0];
}

export function buildFileTree(knownFiles: string[], activeFile?: string): string {
  const lines = ['toy-repo/'];
  for (const file of knownFiles) {
    const marker = file === activeFile ? ' ← active' : '';
    lines.push(`  ${file}${marker}`);
  }
  return lines.join('\n');
}

export function terminalContent(event: TraceEvent): string {
  if (event.terminalOutput) {
    const prefix = event.command ? `$ ${event.command}\n\n` : '';
    const exit = event.exitCode !== undefined ? `\n\nexit code ${event.exitCode}` : '';
    return `${prefix}${event.terminalOutput}${exit}`;
  }
  if (event.command) {
    const exit = event.exitCode !== undefined ? `\nexit code ${event.exitCode}` : '';
    return `$ ${event.command}${exit}`;
  }
  return 'No terminal output for this step.';
}

export function diffContent(event: TraceEvent): string {
  if (event.diff) {
    const header = event.file ? `# ${event.file}\n\n` : '';
    return `${header}${event.diff}`;
  }
  return 'No diff for this step.';
}

export function stepHarnessNote(event: TraceEvent, policyName: string): string | undefined {
  if (event.harnessNote) return event.harnessNote;
  if (event.label === 'ignored_test_output') {
    return `${policyName} allows immediate retry without inspecting failure output.`;
  }
  if (event.label === 'loop_detected') {
    return 'Repeated failed command without new information.';
  }
  if (event.label === 'failed_recovery_guard_triggered') {
    return 'Guarded recovery requires inspecting the failing assertion before retry.';
  }
  return undefined;
}
