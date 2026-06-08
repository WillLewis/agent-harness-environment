import clsx from 'clsx';
import { cardReliability, runsPerCell, type ModelTierPoint } from '../lib/separationReliability';

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function toneFor(value: number) {
  if (value >= 0.85) return 'text-success';
  if (value >= 0.5) return 'text-warning';
  return 'text-danger';
}

function barColor(value: number) {
  if (value >= 0.85) return 'bg-success';
  if (value >= 0.5) return 'bg-warning';
  return 'bg-danger';
}

/** Paired bars for one model: flat visible reference over the real held-out fraction. */
function ModelBars({ point }: { point: ModelTierPoint }) {
  return (
    <div className="space-y-2">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-xs font-medium text-text">{point.modelLabel}</span>
        <span className={clsx('font-mono text-[11px] tabular-nums', toneFor(point.heldOut))}>
          {pct(point.heldOut)}
        </span>
      </div>
      <div className="space-y-1">
        {/* Visible — flat ~100% for every model */}
        <div className="flex items-center gap-2">
          <span className="w-12 shrink-0 font-mono text-[9px] uppercase tracking-wider text-text-faint">visible</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-2">
            <div className="h-full rounded-full bg-text-faint/50" style={{ width: `${point.visible * 100}%` }} />
          </div>
          <span className="w-9 shrink-0 text-right font-mono text-[9px] tabular-nums text-text-faint">
            {pct(point.visible)}
          </span>
        </div>
        {/* Held-out — the true gradient across the model tier */}
        <div className="flex items-center gap-2">
          <span className="w-12 shrink-0 font-mono text-[9px] uppercase tracking-wider text-text-faint">held-out</span>
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-surface-2">
            <div
              className={clsx('h-full rounded-full', barColor(point.heldOut))}
              style={{ width: `${point.heldOut * 100}%` }}
            />
          </div>
          <span className={clsx('w-9 shrink-0 text-right font-mono text-[9px] tabular-nums', toneFor(point.heldOut))}>
            {pct(point.heldOut)}
          </span>
        </div>
      </div>
    </div>
  );
}

export function ReliabilityPanel() {
  return (
    <div className="surface-card mt-6 overflow-hidden">
      <div className="border-b border-border-subtle p-4 sm:p-5">
        <p className="section-chapter">
          <span className="text-text-muted">07</span>
          <span className="mx-2 text-text-muted">·</span>
          <span className="section-label">Reliability · {runsPerCell} held-out runs / model / card</span>
        </p>
        <h3 className="mt-2 text-xl font-semibold text-text sm:text-2xl">Visible says 100%. Held-out reveals the gradient.</h3>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-muted sm:text-sm">
          Each card is one task, run across the model tier (GPT-5.4-nano → Opus 4.8). The{' '}
          <span className="text-text">visible suite passes for every model</span> — that bar is flat at ~100% top to
          bottom. The harness&apos;s <span className="text-text">held-out battery</span> is what separates real
          capability: the lower bar is the mean fraction of held-out items each model actually satisfies.
        </p>
      </div>

      <div className="grid gap-px bg-border-subtle sm:grid-cols-3">
        {cardReliability.map((card) => (
          <div key={card.taskId} className="bg-page/40 p-4 sm:p-5">
            <h4 className="text-sm font-semibold text-text">{card.cardLabel}</h4>
            <p className="mt-1 font-mono text-[10px] uppercase tracking-wider text-text-faint">{card.axis}</p>
            <div className="mt-4 space-y-3.5">
              {card.models.map((point) => (
                <ModelBars key={point.model} point={point} />
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-border-subtle px-4 py-3 text-[11px] leading-relaxed text-text-faint sm:px-5">
        Baseline policy. The guarded_recovery policy barely moves these held-out fractions (the gap is capability, not
        recovery), so it isn&apos;t charted here. Measured, not modeled: each cell is {runsPerCell} real-model runs scored by
        actual execution against the held-out suite.
      </div>
    </div>
  );
}
