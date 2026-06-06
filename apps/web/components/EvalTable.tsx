'use client';

import { useState } from 'react';
import clsx from 'clsx';
import {
  BASELINE_LOOP_CLUSTER_ID,
  BASELINE_UNSAFE_CLUSTER_ID,
  getFailureCluster,
  policyComparison,
  policyDisplayName,
  type FailureClusterId
} from '../lib/evalFixtures';
import { FailureClusterDrawer } from './FailureClusterDrawer';

function formatPercent(value: number) {
  return `${value}%`;
}

type MetricCellProps = {
  value: string;
  clickable?: boolean;
  onClick?: () => void;
  ariaLabel?: string;
  variant?: 'default' | 'alert';
};

function MetricCell({ value, clickable, onClick, ariaLabel, variant = 'default' }: MetricCellProps) {
  if (!clickable || !onClick) {
    return (
      <span className={clsx('font-mono tabular-nums', variant === 'alert' ? 'text-danger' : 'text-text-muted')}>
        {value}
      </span>
    );
  }

  return (
    <button
      type="button"
      className="focus-ring rounded font-mono text-xs tabular-nums text-warning underline decoration-dotted decoration-warning/60 underline-offset-2 transition-colors hover:text-text"
      onClick={onClick}
      aria-label={ariaLabel}
    >
      {value}
    </button>
  );
}

export function EvalTable() {
  const [clusterId, setClusterId] = useState<FailureClusterId | null>(null);
  const selectedCluster = clusterId ? getFailureCluster(clusterId) ?? null : null;

  return (
    <>
      <div className="surface-card overflow-hidden">
        <div className="border-b border-border-subtle p-4 sm:p-5">
          <p className="section-chapter">
            <span className="text-text-muted">07</span>
            <span className="mx-2 text-text-muted">—</span>
            <span className="section-label">Policy comparison · 32 synthetic coding tasks</span>
          </p>
          <h3 className="mt-2 text-xl font-semibold text-text sm:text-2xl">Eval report</h3>
          <p className="mt-2 max-w-3xl text-xs leading-relaxed text-text-muted sm:text-sm">
            Hosted metrics are precomputed synthetic fixtures. They show how eval signals map to harness changes — not
            live production results. Same model, same task, different harness, different outcome.
          </p>
        </div>

        <p className="border-b border-border-subtle px-4 py-2.5 font-mono text-[10px] text-text-faint md:hidden sm:px-5">
          Swipe horizontally to view all policy columns.
        </p>
        <div className="overflow-x-auto overscroll-x-contain">
          <table className="w-full min-w-[720px] text-left text-sm sm:min-w-[860px]" aria-describedby="eval-fixture-note">
            <caption id="eval-fixture-note" className="sr-only">
              Synthetic policy comparison fixture with clickable baseline loop and unsafe-attempt metrics opening failure
              cluster drawers.
            </caption>
            <thead className="bg-surface-2/60 font-mono text-[10px] uppercase tracking-wider text-text-faint">
              <tr>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Policy
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Success
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Recovery
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Loop
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Hallucinated files
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Unsafe attempts
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Human interventions
                </th>
                <th scope="col" className="px-4 py-3 sm:px-5">
                  Cost
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {policyComparison.map((row) => {
                const isBaseline = row.policy === 'baseline';
                const loopValue = formatPercent(row.loop);
                const unsafeValue = formatPercent(row.unsafeAttempts);

                return (
                  <tr key={row.policy} className="transition hover:bg-surface-2/60">
                    <th scope="row" className="px-4 py-3 text-sm font-semibold text-text sm:px-5">
                      {policyDisplayName(row.policy)}
                    </th>
                    <td className="px-4 py-3 font-mono text-xs tabular-nums text-text-muted sm:px-5">
                      {formatPercent(row.success)}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs tabular-nums text-text-muted sm:px-5">
                      {formatPercent(row.recovery)}
                    </td>
                    <td className="px-4 py-3 sm:px-5">
                      <MetricCell
                        value={loopValue}
                        clickable={isBaseline}
                        variant={isBaseline ? 'alert' : 'default'}
                        onClick={isBaseline ? () => setClusterId(BASELINE_LOOP_CLUSTER_ID) : undefined}
                        ariaLabel={
                          isBaseline
                            ? `Open repeated terminal command failure cluster for baseline loop rate ${loopValue}`
                            : undefined
                        }
                      />
                    </td>
                    <td className="px-4 py-3 font-mono text-xs tabular-nums text-text-muted sm:px-5">
                      {formatPercent(row.hallucinatedFiles)}
                    </td>
                    <td className="px-4 py-3 sm:px-5">
                      <MetricCell
                        value={unsafeValue}
                        clickable={isBaseline}
                        variant={isBaseline ? 'alert' : 'default'}
                        onClick={isBaseline ? () => setClusterId(BASELINE_UNSAFE_CLUSTER_ID) : undefined}
                        ariaLabel={
                          isBaseline
                            ? `Open unsafe tool attempt failure cluster for baseline unsafe rate ${unsafeValue}`
                            : undefined
                        }
                      />
                    </td>
                    <td className="px-4 py-3 font-mono text-xs tabular-nums text-text-muted sm:px-5">
                      {row.humanInterventions}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-text-faint sm:px-5">{row.costTier}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="border-t border-border-subtle px-4 py-3 text-[11px] leading-relaxed text-text-faint sm:px-5">
          Click baseline loop or unsafe-attempt metrics to inspect failure clusters, detection rules, and dataset
          candidates. For measured scores on curated trace fixtures, run{' '}
          <code className="text-text-muted">pnpm eval:suite</code> or{' '}
          <code className="text-text-muted">pnpm eval:ci</code> locally — not this synthetic table.
        </div>
      </div>

      <FailureClusterDrawer
        cluster={selectedCluster}
        open={selectedCluster !== null}
        onClose={() => setClusterId(null)}
      />
    </>
  );
}
