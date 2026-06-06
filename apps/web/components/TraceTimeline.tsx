import clsx from 'clsx';
import type { TraceEvent } from '../lib/demoData';
import { stepHarnessNote } from '../lib/cockpitEvidence';
import { selectableActiveClass, selectableIdleClass } from '../lib/statusStyles';

type TraceTimelineProps = {
  events: TraceEvent[];
  activeStep: number;
  onSelect: (step: number) => void;
  policyName: string;
};

export function TraceTimeline({ events, activeStep, onSelect, policyName }: TraceTimelineProps) {
  return (
    <div className="space-y-1.5" role="list" aria-label="Trace timeline">
      {events.map((event) => {
        const active = event.step === activeStep;
        const harnessNote = stepHarnessNote(event, policyName);
        const stepLabel = `Step ${String(event.step).padStart(2, '0')}: ${event.title}`;

        return (
          <button
            key={event.id}
            type="button"
            role="listitem"
            aria-current={active ? 'step' : undefined}
            aria-label={event.label ? `${stepLabel}, ${event.label}` : stepLabel}
            onClick={() => onSelect(event.step)}
            className={clsx(
              'focus-ring w-full rounded-lg border p-3 text-left transition',
              active ? selectableActiveClass : selectableIdleClass
            )}
          >
            <div className="flex min-w-0 items-start justify-between gap-2">
              <div className="min-w-0 flex-1">
                <div className="font-mono text-[10px] text-text-faint">
                  STEP {String(event.step).padStart(2, '0')} · {event.action}
                </div>
                <div className="mt-0.5 break-words text-sm font-semibold text-text">{event.title}</div>
              </div>
              {event.label ? (
                <span className="shrink-0 rounded border border-warning/30 bg-warning/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wide text-warning">
                  {event.label}
                </span>
              ) : null}
            </div>
            <p className="mt-1.5 break-words text-xs leading-5 text-text-muted">{event.summary}</p>
            {active && harnessNote ? (
              <p className="mt-2 break-words rounded-md border border-border-subtle bg-code-bg px-2.5 py-2 text-[11px] leading-5 text-text-faint">
                Harness note: {harnessNote}
              </p>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
