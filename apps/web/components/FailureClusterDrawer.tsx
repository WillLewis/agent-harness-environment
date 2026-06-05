'use client';

import { useEffect, useRef, type ReactNode } from 'react';
import clsx from 'clsx';
import type { FailureCluster } from '../lib/evalFixtures';

type FailureClusterDrawerProps = {
  cluster: FailureCluster | null;
  open: boolean;
  onClose: () => void;
};

function severityTone(severity: string) {
  if (severity === 'high') return 'border-red-300/30 bg-red-300/10 text-red-100';
  if (severity === 'medium') return 'border-amber-300/30 bg-amber-300/10 text-amber-100';
  return 'border-slate-300/30 bg-slate-300/10 text-slate-100';
}

function DetailBlock({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</div>
      <div className="mt-2 text-sm leading-6 text-slate-200">{children}</div>
    </div>
  );
}

export function FailureClusterDrawer({ cluster, open, onClose }: FailureClusterDrawerProps) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;

    closeRef.current?.focus();

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose();
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    document.addEventListener('keydown', onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open, onClose]);

  if (!open || !cluster) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button
        type="button"
        className="absolute inset-0 bg-black/60"
        aria-label="Close failure cluster detail"
        onClick={onClose}
      />

      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="failure-cluster-title"
        className="relative z-10 flex h-full w-full max-w-xl flex-col border-l border-white/10 bg-[#0a1018] shadow-2xl"
      >
        <div className="flex items-start justify-between gap-4 border-b border-white/10 p-5">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Failure cluster</p>
            <h3 id="failure-cluster-title" className="mt-2 text-2xl font-semibold text-white">
              {cluster.label}
            </h3>
            <p className="mt-1 font-mono text-xs text-slate-500">{cluster.id}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            className="focus-ring rounded-full border border-white/10 px-3 py-1.5 text-xs text-slate-300"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto p-5">
          <div className="flex flex-wrap items-center gap-2">
            <span className={clsx('rounded-full border px-2.5 py-1 text-xs uppercase tracking-wide', severityTone(cluster.severity))}>
              {cluster.severity} severity
            </span>
            <span className="rounded-full border border-white/10 px-2.5 py-1 font-mono text-xs text-slate-300">
              {cluster.frequency}% of baseline failures
            </span>
          </div>

          <DetailBlock label="Pattern">{cluster.pattern}</DetailBlock>
          <DetailBlock label="Detection rule">
            <code className="block rounded-2xl border border-white/10 bg-black/30 p-3 font-mono text-xs leading-6 text-cyan-100">
              {cluster.detectionRule}
            </code>
          </DetailBlock>
          <DetailBlock label="Affected tasks">
            <ul className="space-y-1 font-mono text-xs text-slate-300">
              {cluster.affectedTasks.map((taskId) => (
                <li key={taskId}>• {taskId}</li>
              ))}
            </ul>
          </DetailBlock>
          <DetailBlock label="Recommended harness change">{cluster.recommendedHarnessChange}</DetailBlock>

          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Dataset candidate</div>
            <p className="mt-2 text-xs leading-5 text-slate-400">
              Promote-to-dataset preview from fixture data. Copy or inspect the JSON below.
            </p>
            <pre className="mt-3 overflow-auto rounded-2xl border border-white/10 bg-black/40 p-4 font-mono text-xs leading-6 text-slate-300">
              {JSON.stringify(cluster.datasetCandidate, null, 2)}
            </pre>
          </div>
        </div>

        <div className="border-t border-white/10 p-5 text-xs leading-5 text-slate-500">
          Trace → failure cluster → dataset coverage → harness improvement → re-eval
        </div>
      </aside>
    </div>
  );
}
