import clsx from 'clsx';
import { policyDisplayName, reliability, reliabilityPolicy } from '../lib/evalFixtures';

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function toneFor(value: number) {
  if (value >= 0.85) return 'text-success';
  if (value >= 0.5) return 'text-warning';
  return 'text-danger';
}

function DotStrip({ flags, label }: { flags: boolean[]; label: string }) {
  const passed = flags.filter(Boolean).length;
  return (
    <div className="flex items-center gap-3">
      <span className="w-16 shrink-0 font-mono text-[10px] uppercase tracking-wider text-text-faint">{label}</span>
      <div className="flex flex-wrap gap-1">
        {flags.map((flag, index) => (
          <span
            key={index}
            className={clsx('h-2 w-2 rounded-full', flag ? 'bg-success' : 'bg-danger/80')}
            aria-hidden="true"
          />
        ))}
      </div>
      <span className="ml-auto shrink-0 font-mono text-[10px] text-text-faint">
        {passed}/{flags.length}
      </span>
    </div>
  );
}

export function ReliabilityPanel() {
  const baseline = reliabilityPolicy('baseline');
  const guarded = reliabilityPolicy('guarded_recovery');

  return (
    <div className="surface-card mt-6 overflow-hidden">
      <div className="border-b border-border-subtle p-4 sm:p-5">
        <p className="section-chapter">
          <span className="text-text-muted">07</span>
          <span className="mx-2 text-text-muted">·</span>
          <span className="section-label">Reliability · {reliability.n} real seeded runs / policy</span>
        </p>
        <h3 className="mt-2 text-xl font-semibold text-text sm:text-2xl">Naive metric vs. held-out truth</h3>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-muted sm:text-sm">
          Each cell is {reliability.n} real runs of the date-parser task (capability {reliability.capability}) scored by
          actual <code className="text-text-muted">npm test</code> plus a harness-only held-out suite.{' '}
          <span className="text-text">Visible</span> is what an eval that only runs the agent&apos;s own test would
          report; <span className="text-text">held-out</span> is whether the patch actually generalizes.{' '}
          <span className="font-mono">pass^k</span> is the probability all k of k attempts pass.
        </p>
      </div>

      <div className="overflow-x-auto overscroll-x-contain">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead className="bg-surface-2/60 font-mono text-[10px] uppercase tracking-wider text-text-faint">
            <tr>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Policy
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Visible pass@1
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Held-out pass@1
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Held-out pass^5
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {reliability.policies.map((row) => (
              <tr key={row.policy} className="transition hover:bg-surface-2/60">
                <th scope="row" className="px-4 py-3 text-sm font-semibold text-text sm:px-5">
                  {policyDisplayName(row.policy)}
                </th>
                <td className="px-4 py-3 font-mono text-xs tabular-nums text-text-muted sm:px-5">
                  {pct(row.visible.pass1)}
                </td>
                <td className={clsx('px-4 py-3 font-mono text-xs tabular-nums sm:px-5', toneFor(row.heldOut.pass1))}>
                  {pct(row.heldOut.pass1)}
                </td>
                <td
                  className={clsx('px-4 py-3 font-mono text-xs tabular-nums sm:px-5', toneFor(row.heldOut.passK['5']))}
                >
                  {row.heldOut.passK['5'].toFixed(3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {baseline && guarded ? (
        <div className="space-y-4 border-t border-border-subtle p-4 sm:p-5">
          <p className="font-mono text-[10px] uppercase tracking-widest text-text-faint">
            per-seed outcomes · green = pass · red = fail
          </p>
          {[baseline, guarded].map((row) => (
            <div key={row.policy} className="space-y-1.5">
              <p className="text-xs font-semibold text-text">{policyDisplayName(row.policy)}</p>
              <DotStrip flags={row.seedResults.visible} label="visible" />
              <DotStrip flags={row.seedResults.heldOut} label="held-out" />
            </div>
          ))}
        </div>
      ) : null}

      <div className="border-t border-border-subtle px-4 py-3 text-[11px] leading-relaxed text-text-faint sm:px-5">
        Measured, not modeled: regenerate with <code className="text-text-muted">python packages/evals/pass_k.py</code>.
        Magnitudes are illustrative (decision-point weights are hand-set); the orderings — held-out ≤ visible, and
        guarded pass^k ≫ baseline — are structural.
      </div>
    </div>
  );
}
