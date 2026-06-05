import clsx from 'clsx';
import type { TraceEvent } from '../lib/demoData';
import { stepHarnessNote } from '../lib/cockpitEvidence';

type TraceTimelineProps = {
  events: TraceEvent[];
  activeStep: number;
  onSelect: (step: number) => void;
  policyName: string;
};

export function TraceTimeline({ events, activeStep, onSelect, policyName }: TraceTimelineProps) {
  return (
    <div className="space-y-2" role="list" aria-label="Trace timeline">
      {events.map((event) => {
        const active = event.step === activeStep;
        const harnessNote = stepHarnessNote(event, policyName);

        return (
          <button
            key={event.id}
            type="button"
            role="listitem"
            aria-current={active ? 'step' : undefined}
            onClick={() => onSelect(event.step)}
            className={clsx(
              'focus-ring w-full rounded-2xl border p-4 text-left transition',
              active ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.06]'
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-mono text-xs text-slate-500">
                  STEP {String(event.step).padStart(2, '0')} · {event.action}
                </div>
                <div className="mt-1 font-semibold text-white">{event.title}</div>
              </div>
              {event.label ? (
                <span className="rounded-full border border-amber-300/30 bg-amber-300/10 px-2 py-1 font-mono text-[10px] uppercase tracking-wide text-amber-200">
                  {event.label}
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">{event.summary}</p>
            {active && harnessNote ? (
              <p className="mt-2 rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs leading-5 text-slate-400">
                Harness note: {harnessNote}
              </p>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
