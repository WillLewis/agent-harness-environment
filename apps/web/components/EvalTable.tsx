import clsx from 'clsx';
import { cardReliability, modelLabel, modelOrder, runsPerCell } from '../lib/separationReliability';

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function toneFor(value: number) {
  if (value >= 0.85) return 'text-success';
  if (value >= 0.5) return 'text-warning';
  return 'text-danger';
}

export function EvalTable() {
  return (
    <div className="surface-card overflow-hidden">
      <div className="border-b border-border-subtle p-4 sm:p-5">
        <p className="section-chapter">
          <span className="text-text-muted">07</span>
          <span className="mx-2 text-text-muted">—</span>
          <span className="section-label">Held-out eval · card × model · baseline policy</span>
        </p>
        <h3 className="mt-2 text-xl font-semibold text-text sm:text-2xl">Eval report</h3>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-muted sm:text-sm">
          One row per task, one column per model (GPT-5.4-nano → Opus 4.8). The{' '}
          <span className="text-text">Visible</span> column is the agent&apos;s own suite — 100% for every model. The
          per-model cells are the <span className="text-text">held-out mean-fraction</span>: same task, same visible
          pass, different model, different real outcome.
        </p>
      </div>

      <p className="border-b border-border-subtle px-4 py-2.5 font-mono text-[10px] text-text-faint md:hidden sm:px-5">
        Swipe horizontally to view all model columns.
      </p>
      <div className="overflow-x-auto overscroll-x-contain">
        <table className="w-full min-w-[720px] text-left text-sm sm:min-w-[860px]" aria-describedby="eval-fixture-note">
          <caption id="eval-fixture-note" className="sr-only">
            Held-out eval fixture: one row per task, Visible pass rate plus held-out mean-fraction per model, baseline
            policy.
          </caption>
          <thead className="bg-surface-2/60 font-mono text-[10px] uppercase tracking-wider text-text-faint">
            <tr>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Task
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Visible
              </th>
              {modelOrder.map((model) => (
                <th key={model} scope="col" className="px-4 py-3 sm:px-5">
                  {modelLabel(model)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {cardReliability.map((card) => (
              <tr key={card.taskId} className="transition hover:bg-surface-2/60">
                <th scope="row" className="px-4 py-3 sm:px-5">
                  <span className="block text-sm font-semibold text-text">{card.cardLabel}</span>
                  <span className="mt-0.5 block font-mono text-[10px] text-text-faint">{card.axis}</span>
                </th>
                <td className="px-4 py-3 font-mono text-xs tabular-nums text-text-faint sm:px-5">100%</td>
                {modelOrder.map((model) => {
                  const point = card.models.find((p) => p.model === model);
                  return (
                    <td key={model} className="px-4 py-3 sm:px-5">
                      {point ? (
                        <span className={clsx('font-mono text-xs tabular-nums', toneFor(point.heldOut))}>
                          {formatPercent(point.heldOut)}
                        </span>
                      ) : (
                        <span className="font-mono text-xs text-text-faint">—</span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="border-t border-border-subtle px-4 py-3 text-[11px] leading-relaxed text-text-faint sm:px-5">
        Each cell is {runsPerCell} real-model runs scored by actual execution against the held-out suite (baseline policy).
        Visible is flat at 100% by construction — the visible suite passes for every model. For measured scores on
        curated trace fixtures, run <code className="text-text-muted">pnpm eval:suite</code> or{' '}
        <code className="text-text-muted">pnpm eval:ci</code> locally.
      </div>
    </div>
  );
}
