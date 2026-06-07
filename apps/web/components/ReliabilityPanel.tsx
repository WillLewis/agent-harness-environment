'use client';

import clsx from 'clsx';
import { useState } from 'react';
import { policyDisplayName, reliability, reliabilityPolicy, reliabilityTasks } from '../lib/evalFixtures';

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
  const [taskId, setTaskId] = useState(reliabilityTasks[0]?.task_id);
  const task = reliabilityTasks.find((row) => row.task_id === taskId) ?? reliabilityTasks[0];
  const baseline = reliabilityPolicy(task, 'baseline');
  const guarded = reliabilityPolicy(task, 'guarded_recovery');

  return (
    <div className="surface-card mt-6 overflow-hidden">
      <div className="border-b border-border-subtle p-4 sm:p-5">
        <p className="section-chapter">
          <span className="text-text-muted">07</span>
          <span className="mx-2 text-text-muted">·</span>
          <span className="section-label">Reliability · {reliability.n} real seeded runs / cell</span>
        </p>
        <h3 className="mt-2 text-xl font-semibold text-text sm:text-2xl">Naive metric vs. held-out truth</h3>
        <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-muted sm:text-sm">
          Each cell is {reliability.n} real seeded runs (capability {task.capability}) scored by actual execution.{' '}
          <span className="text-text">{task.visibleLabel}</span> is what an eval that only runs the agent&apos;s own
          checks would report; <span className="text-text">{task.heldOutLabel}</span> is the true outcome.{' '}
          <span className="font-mono">pass^k</span> is the probability all k of k attempts pass.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {reliabilityTasks.map((row) => (
            <button
              key={row.task_id}
              type="button"
              onClick={() => setTaskId(row.task_id)}
              className={clsx(
                'rounded-full border px-3 py-1 text-xs font-medium transition',
                row.task_id === task.task_id
                  ? 'border-border-strong bg-surface-2 text-text'
                  : 'border-border-subtle text-text-muted hover:bg-surface-2/60'
              )}
            >
              {row.label}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto overscroll-x-contain">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead className="bg-surface-2/60 font-mono text-[10px] uppercase tracking-wider text-text-faint">
            <tr>
              <th scope="col" className="px-4 py-3 sm:px-5">
                Policy
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                {task.visibleLabel} pass@1
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                {task.heldOutLabel} pass@1
              </th>
              <th scope="col" className="px-4 py-3 sm:px-5">
                {task.heldOutLabel} pass^5
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border-subtle">
            {task.policies.map((row) => (
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
        {task.metric_note} Measured, not modeled: regenerate with{' '}
        <code className="text-text-muted">python packages/evals/pass_k.py</code>. Magnitudes are illustrative
        (decision-point weights are hand-set); the orderings — held-out ≤ visible, and guarded pass^k ≫ baseline — are
        structural.
      </div>
    </div>
  );
}
