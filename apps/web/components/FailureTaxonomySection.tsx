'use client';

import { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import {
  failureClusters,
  getFailureCluster,
  type FailureClusterId
} from '../lib/evalFixtures';
import { FailureClusterDrawer } from './FailureClusterDrawer';
import { SectionHeader } from './SectionHeader';

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
          chapter="06"
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
            <button
              key={cluster.id}
              type="button"
              onClick={() => setClusterId(cluster.id)}
              aria-label={`Inspect failure cluster: ${cluster.label}`}
              className="focus-ring group flex flex-col rounded-xl border border-border-subtle bg-surface/50 p-4 text-left transition-colors hover:bg-surface-2/60 sm:p-5"
            >
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-base font-medium text-text">{cluster.label}</h3>
                <span className="shrink-0 rounded-md border border-border-subtle bg-surface-2 px-2 py-0.5 font-mono text-[10px] text-text-muted">
                  {cluster.frequency} hits
                </span>
              </div>
              <p className="mt-1.5 flex-1 text-sm leading-relaxed text-text-muted">{cluster.pattern}</p>
              <div className="mt-3 inline-flex items-center gap-1 text-xs text-accent-muted">
                Inspect cluster
                <ChevronRight className="size-3 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
              </div>
            </button>
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
