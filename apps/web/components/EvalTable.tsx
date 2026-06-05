'use client';

import { useState } from 'react';
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
};

function MetricCell({ value, clickable, onClick, ariaLabel }: MetricCellProps) {
  if (!clickable || !onClick) {
    return <span className="text-slate-300">{value}</span>;
  }

  return (
    <button
      type="button"
      className="focus-ring rounded-md border border-cyan-300/20 bg-cyan-300/5 px-2 py-1 font-mono text-cyan-100 underline decoration-cyan-300/40 underline-offset-4 hover:bg-cyan-300/10"
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
      <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03]">
        <div className="border-b border-white/10 p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Policy comparison · 32 synthetic coding tasks</p>
          <h3 className="mt-2 text-2xl font-semibold text-white">Eval report</h3>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
            Hosted metrics are precomputed synthetic fixtures. They show how eval signals map to harness changes — not live
            production results. Same model, same task, different harness, different outcome.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] text-left text-sm" aria-describedby="eval-fixture-note">
            <caption id="eval-fixture-note" className="sr-only">
              Synthetic policy comparison fixture with clickable baseline loop and unsafe-attempt metrics opening
              failure cluster drawers.
            </caption>
            <thead className="bg-white/[0.04] text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th scope="col" className="px-5 py-4">
                  Policy
                </th>
                <th scope="col" className="px-5 py-4">
                  Success
                </th>
                <th scope="col" className="px-5 py-4">
                  Recovery
                </th>
                <th scope="col" className="px-5 py-4">
                  Loop
                </th>
                <th scope="col" className="px-5 py-4">
                  Hallucinated files
                </th>
                <th scope="col" className="px-5 py-4">
                  Unsafe attempts
                </th>
                <th scope="col" className="px-5 py-4">
                  Human interventions
                </th>
                <th scope="col" className="px-5 py-4">
                  Cost
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {policyComparison.map((row) => {
                const isBaseline = row.policy === 'baseline';
                const loopValue = formatPercent(row.loop);
                const unsafeValue = formatPercent(row.unsafeAttempts);

                return (
                  <tr key={row.policy} className="hover:bg-white/[0.03]">
                    <th scope="row" className="px-5 py-4 font-semibold text-white">
                      {policyDisplayName(row.policy)}
                    </th>
                    <td className="px-5 py-4 text-slate-300">{formatPercent(row.success)}</td>
                    <td className="px-5 py-4 text-slate-300">{formatPercent(row.recovery)}</td>
                    <td className="px-5 py-4">
                      <MetricCell
                        value={loopValue}
                        clickable={isBaseline}
                        onClick={
                          isBaseline
                            ? () => setClusterId(BASELINE_LOOP_CLUSTER_ID)
                            : undefined
                        }
                        ariaLabel={
                          isBaseline
                            ? `Open repeated terminal command failure cluster for baseline loop rate ${loopValue}`
                            : undefined
                        }
                      />
                    </td>
                    <td className="px-5 py-4 text-slate-300">{formatPercent(row.hallucinatedFiles)}</td>
                    <td className="px-5 py-4">
                      <MetricCell
                        value={unsafeValue}
                        clickable={isBaseline}
                        onClick={isBaseline ? () => setClusterId(BASELINE_UNSAFE_CLUSTER_ID) : undefined}
                        ariaLabel={
                          isBaseline
                            ? `Open unsafe tool attempt failure cluster for baseline unsafe rate ${unsafeValue}`
                            : undefined
                        }
                      />
                    </td>
                    <td className="px-5 py-4 text-slate-300">{row.humanInterventions}</td>
                    <td className="px-5 py-4 font-mono text-slate-300">{row.costTier}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="border-t border-white/10 px-5 py-4 text-xs text-slate-500">
          Click baseline loop or unsafe-attempt metrics to inspect failure clusters, detection rules, and dataset
          candidates.
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
