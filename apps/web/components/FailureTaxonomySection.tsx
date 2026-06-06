'use client';

import { useState } from 'react';
import clsx from 'clsx';
import {
  failureClusters,
  getFailureCluster,
  type FailureClusterId
} from '../lib/evalFixtures';
import { FailureClusterDrawer } from './FailureClusterDrawer';
import { SectionHeader } from './SectionHeader';
import { SurfaceCard } from './ui/SurfaceCard';
import { severityBadgeClass } from '../lib/statusStyles';

export function FailureTaxonomySection() {
  const [clusterId, setClusterId] = useState<FailureClusterId | null>(null);
  const selectedCluster = clusterId ? getFailureCluster(clusterId) ?? null : null;

  return (
    <>
      <section
        id="failure-taxonomy"
        className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8"
        aria-label="Failure taxonomy"
      >
        <SectionHeader
          chapter="05"
          label="failure taxonomy"
          title="The same shapes, over and over"
          description={
            <>
              Cluster metadata from{' '}
              <span className="font-mono text-text-muted">data/failure_clusters.json</span>. Frequencies are fixture
              illustration counts — not production telemetry. Click a cluster to inspect detection rules and harness
              recommendations; red eval cells open the same detail from the table below.
            </>
          }
          className="mb-8"
        />
        <div className="grid gap-3 md:grid-cols-2">
          {failureClusters.map((cluster) => (
            <SurfaceCard key={cluster.id} className="flex flex-col">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <h3 className="text-base font-semibold text-text">{cluster.label}</h3>
                <span
                  className={clsx(
                    'rounded-md border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide',
                    severityBadgeClass(cluster.severity)
                  )}
                >
                  {cluster.severity}
                </span>
              </div>
              <p className="mt-2 flex-1 text-sm leading-relaxed text-text-muted">{cluster.pattern}</p>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <span className="font-mono text-xs text-text-faint">{cluster.frequency} fixture hits</span>
                <button
                  type="button"
                  className="focus-ring rounded-md border border-border-subtle bg-surface-2 px-3 py-1.5 font-mono text-xs text-accent-muted hover:bg-surface-raised"
                  onClick={() => setClusterId(cluster.id)}
                  aria-label={`Inspect failure cluster: ${cluster.label}`}
                >
                  Inspect cluster
                </button>
              </div>
            </SurfaceCard>
          ))}
        </div>
      </section>

      <FailureClusterDrawer
        cluster={selectedCluster}
        open={selectedCluster !== null}
        onClose={() => setClusterId(null)}
      />
    </>
  );
}
