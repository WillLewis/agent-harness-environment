import clsx from 'clsx';
import type { ReactNode } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  FileCode,
  FileSearch,
  FileText,
  GitBranch,
  RotateCcw,
  Search,
  ShieldCheck,
  Terminal,
  Wrench,
  XCircle
} from 'lucide-react';
import type { TraceEvent } from '../lib/demoData';
import { stepHarnessNote } from '../lib/cockpitEvidence';

type TraceTimelineProps = {
  events: TraceEvent[];
  activeStep: number;
  onSelect: (step: number) => void;
  policyName: string;
  renderAfterEvent?: (event: TraceEvent) => ReactNode;
};

const eventIcons = {
  PLAN: FileText,
  READ_FILE: FileSearch,
  SEARCH: Search,
  EDIT: FileCode,
  TERMINAL: Terminal,
  TEST: XCircle,
  RETRY: RotateCcw,
  ASK_USER: GitBranch,
  BLOCKED_ACTION: AlertTriangle,
  POLICY_DECISION: ShieldCheck,
  FINAL: ShieldCheck
} as const;

const toneClasses = {
  neutral: 'border-border bg-surface-2 text-text',
  ok: 'border-success/40 bg-success/10 text-success',
  warn: 'border-warning/40 bg-warning/10 text-warning',
  info: 'border-info/40 bg-info/10 text-info',
  assist: 'border-assist/40 bg-assist/10 text-assist'
} as const;

function eventTone(event: TraceEvent): keyof typeof toneClasses {
  if (event.action === 'ASK_USER') return 'assist';
  if (event.action === 'POLICY_DECISION' || event.action === 'READ_FILE' || event.action === 'SEARCH') return 'info';
  if (event.action === 'BLOCKED_ACTION' || event.action === 'RETRY') return 'warn';
  if (event.action === 'TEST') return event.exitCode === 0 ? 'ok' : 'warn';
  if (event.action === 'FINAL') {
    const verdict = typeof event.raw?.verdict === 'string' ? event.raw.verdict : undefined;
    return verdict === 'accepted' || verdict === 'assisted' ? 'ok' : 'warn';
  }
  return 'neutral';
}

export function TraceTimeline({ events, activeStep, onSelect, policyName, renderAfterEvent }: TraceTimelineProps) {
  return (
    <ol className="space-y-1.5" aria-label="Trace timeline">
      {events.map((event) => {
        const active = event.step === activeStep;
        const harnessNote = stepHarnessNote(event, policyName);
        const stepLabel = `Step ${String(event.step).padStart(2, '0')}: ${event.title}`;
        const tone = eventTone(event);
        const Icon = event.action === 'TEST' && event.exitCode === 0 ? CheckCircle2 : eventIcons[event.action] ?? FileText;

        return (
          <li key={event.id}>
            <button
              type="button"
              aria-current={active ? 'step' : undefined}
              aria-label={event.label ? `${stepLabel}, ${event.label}` : stepLabel}
              onClick={() => onSelect(event.step)}
              className={clsx(
                'focus-ring flex w-full items-start gap-3 rounded-md border px-3 py-2 text-left transition-all',
                active ? `${toneClasses[tone]} ring-1 ring-text/10` : 'border-border-subtle bg-transparent opacity-60 hover:bg-surface-2/50 hover:opacity-90'
              )}
            >
              <Icon className={clsx('mt-0.5 size-4 shrink-0', active ? '' : 'text-text-faint')} aria-hidden="true" />
              <div className="min-w-0 flex-1">
                <div className="flex min-w-0 items-center gap-2 font-mono text-[10px] uppercase tracking-wide text-text-faint">
                  <span>STEP {String(event.step).padStart(2, '0')} · {event.action}</span>
                  {event.file ? (
                    <span className="truncate normal-case tracking-normal text-text-faint/80">· {event.file}</span>
                  ) : null}
                </div>
                <div className="mt-0.5 break-words text-sm leading-snug text-text">{event.title}</div>
                <p className="mt-1 break-words text-xs leading-snug text-text-muted">{event.summary}</p>
                {active && harnessNote ? (
                  <p className="mt-2 break-words rounded-md border border-border-subtle bg-code-bg px-2.5 py-2 text-[11px] leading-5 text-text-faint">
                    Harness note: {harnessNote}
                  </p>
                ) : null}
              </div>
              {event.label ? (
                <span className="shrink-0 rounded border border-warning/30 bg-warning/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wide text-warning">
                  {event.label}
                </span>
              ) : null}
            </button>
            {renderAfterEvent ? renderAfterEvent(event) : null}
          </li>
        );
      })}
    </ol>
  );
}
