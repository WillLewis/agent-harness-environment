import clsx from 'clsx';
import type { TraceEvent } from '../lib/demoData';

type TraceTimelineProps = {
  events: TraceEvent[];
  activeStep: number;
  onSelect: (step: number) => void;
};

export function TraceTimeline({ events, activeStep, onSelect }: TraceTimelineProps) {
  return (
    <div className="space-y-2">
      {events.map((event) => {
        const active = event.step === activeStep;
        return (
          <button
            key={event.id}
            type="button"
            onClick={() => onSelect(event.step)}
            className={clsx(
              'focus-ring w-full rounded-2xl border p-4 text-left transition',
              active ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.06]'
            )}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-mono text-xs text-slate-500">STEP {String(event.step).padStart(2, '0')} · {event.action}</div>
                <div className="mt-1 font-semibold text-white">{event.title}</div>
              </div>
              {event.label ? (
                <span className="rounded-full border border-amber-300/30 bg-amber-300/10 px-2 py-1 font-mono text-[10px] uppercase tracking-wide text-amber-200">
                  {event.label}
                </span>
              ) : null}
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">{event.summary}</p>
          </button>
        );
      })}
    </div>
  );
}
