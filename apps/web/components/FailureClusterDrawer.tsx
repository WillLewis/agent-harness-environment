'use client';

import { useEffect, useId, useRef, type ReactNode } from 'react';
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
  const descriptionId = useId();

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
    <div className="fixed inset-0 z-50 flex justify-end" role="presentation">
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
        aria-describedby={descriptionId}
        className="relative z-10 flex h-[100dvh] w-full max-w-full flex-col border-l border-white/10 bg-[#0a1018] shadow-2xl sm:h-full sm:max-w-xl"
      >
        <div className="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-white/10 bg-[#0a1018] p-4 sm:p-5">
          <div className="min-w-0 flex-1">
            <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Failure cluster</p>
            <h3 id="failure-cluster-title" className="mt-2 break-words text-xl font-semibold text-white sm:text-2xl">
              {cluster.label}
            </h3>
            <p className="mt-1 break-all font-mono text-xs text-slate-500">{cluster.id}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            className="focus-ring shrink-0 rounded-full border border-white/10 px-3 py-1.5 text-xs text-slate-300"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <div id={descriptionId} className="flex-1 space-y-5 overflow-y-auto p-4 sm:p-5">
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
            <code className="code-panel block rounded-2xl border border-white/10 bg-black/30 p-3 font-mono text-xs leading-6 text-cyan-100">
              {cluster.detectionRule}
            </code>
          </DetailBlock>
          <DetailBlock label="Affected tasks">
            <ul className="space-y-1 font-mono text-xs text-slate-300">
              {cluster.affectedTasks.map((taskId) => (
                <li key={taskId} className="break-all">
                  • {taskId}
                </li>
              ))}
            </ul>
          </DetailBlock>
          <DetailBlock label="Recommended harness change">
            <p className="break-words">{cluster.recommendedHarnessChange}</p>
          </DetailBlock>

          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Dataset candidate</div>
            <p className="mt-2 text-xs leading-5 text-slate-400">
              Promote-to-dataset preview from fixture data. Copy or inspect the JSON below.
            </p>
            <pre className="code-panel mt-3 max-h-64 rounded-2xl border border-white/10 bg-black/40 p-4 font-mono text-xs leading-6 text-slate-300 sm:max-h-80">
              {JSON.stringify(cluster.datasetCandidate, null, 2)}
            </pre>
          </div>
        </div>

        <div className="border-t border-white/10 p-4 text-xs leading-5 text-slate-500 sm:p-5">
          Trace → failure cluster → dataset coverage → harness improvement → re-eval
        </div>
      </aside>
    </div>
  );
}
