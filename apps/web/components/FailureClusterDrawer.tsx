'use client';

import { useEffect, useId, useRef, type ReactNode } from 'react';
import clsx from 'clsx';
import type { FailureCluster } from '../lib/evalFixtures';
import { severityBadgeClass } from '../lib/statusStyles';

type FailureClusterDrawerProps = {
  cluster: FailureCluster | null;
  open: boolean;
  onClose: () => void;
};

function DetailBlock({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">{label}</div>
      <div className="mt-1.5 text-sm leading-relaxed text-text-muted">{children}</div>
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
        className="absolute inset-0 bg-page/80 backdrop-blur-sm"
        aria-label="Close failure cluster detail"
        onClick={onClose}
      />

      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="failure-cluster-title"
        aria-describedby={descriptionId}
        className="relative z-10 flex h-[100dvh] w-full max-w-full flex-col border-l border-border-subtle bg-elevated shadow-2xl sm:h-full sm:max-w-xl"
      >
        <div className="sticky top-0 z-10 flex items-start justify-between gap-3 border-b border-border-subtle bg-elevated p-4 sm:p-5">
          <div className="min-w-0 flex-1">
            <p className="section-label">Failure cluster</p>
            <h3 id="failure-cluster-title" className="mt-1.5 break-words text-lg font-semibold text-text sm:text-xl">
              {cluster.label}
            </h3>
            <p className="mt-1 break-all font-mono text-[10px] text-text-faint">{cluster.id}</p>
          </div>
          <button
            ref={closeRef}
            type="button"
            className="focus-ring shrink-0 rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[11px] text-text-muted hover:bg-surface-2"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <div id={descriptionId} className="flex-1 space-y-4 overflow-y-auto p-4 sm:p-5">
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={clsx(
                'rounded-md border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wide',
                severityBadgeClass(cluster.severity)
              )}
            >
              {cluster.severity} severity
            </span>
            <span className="rounded-md border border-border-subtle px-2 py-0.5 font-mono text-[10px] text-text-muted">
              {cluster.frequency} fixture hits
            </span>
          </div>

          <DetailBlock label="Pattern">{cluster.pattern}</DetailBlock>
          <DetailBlock label="Detection rule">
            <code className="code-panel mt-1.5 block p-3 font-mono text-[11px] leading-5 text-accent-muted">
              {cluster.detectionRule}
            </code>
          </DetailBlock>
          <DetailBlock label="Affected tasks">
            <ul className="space-y-1 font-mono text-[11px] text-text-muted">
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
            <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Dataset candidate</div>
            <p className="mt-1.5 text-[11px] leading-relaxed text-text-faint">
              Promote-to-dataset preview from fixture data. Copy or inspect the JSON below.
            </p>
            <pre className="code-panel mt-2 max-h-64 p-3 font-mono text-[11px] leading-5 sm:max-h-80">
              {JSON.stringify(cluster.datasetCandidate, null, 2)}
            </pre>
          </div>
        </div>

        <div className="border-t border-border-subtle p-4 font-mono text-[10px] leading-relaxed text-text-faint sm:p-5">
          Trace → failure cluster → dataset coverage → harness improvement → re-eval
        </div>
      </aside>
    </div>
  );
}
