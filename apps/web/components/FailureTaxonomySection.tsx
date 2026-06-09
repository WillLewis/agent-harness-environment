'use client';

import { useEffect, useId, useRef, useState } from 'react';
import clsx from 'clsx';
import { ChevronRight } from 'lucide-react';
import { heldOutFailures, type HeldOutFailure } from '../lib/heldOutFailures';
import { severityBadgeClass } from '../lib/statusStyles';
import { SectionHeader } from './SectionHeader';

function HeldOutFailureDrawer({
  failure,
  open,
  onClose
}: {
  failure: HeldOutFailure | null;
  open: boolean;
  onClose: () => void;
}) {
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

  if (!open || !failure) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end" role="presentation">
      <button
        type="button"
        className="focus-ring absolute inset-0 bg-page/80 backdrop-blur-sm"
        aria-label="Close failure shape detail"
        onClick={onClose}
      />

      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="held-out-failure-title"
        aria-describedby={descriptionId}
        className="relative z-10 flex h-[100dvh] w-full max-w-full flex-col border-l border-border-subtle bg-elevated shadow-2xl sm:h-full sm:max-w-xl"
      >
        <div className="sticky top-0 z-10 flex items-start justify-between gap-3 border-b border-border-subtle bg-elevated p-4 sm:p-5">
          <div className="min-w-0 flex-1">
            <p className="section-label">Held-out failure shape</p>
            <h3 id="held-out-failure-title" className="mt-1.5 break-words text-lg font-semibold text-text sm:text-xl">
              {failure.label}
            </h3>
            <p className="mt-1 break-words font-mono text-[10px] text-text-faint">{failure.card}</p>
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
                severityBadgeClass(failure.severity)
              )}
            >
              {failure.severity} severity
            </span>
            <span className="rounded-md border border-border-subtle px-2 py-0.5 font-mono text-[10px] text-text-muted">
              shows up: {failure.tier}
            </span>
          </div>

          <div>
            <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Pattern</div>
            <p className="mt-1.5 break-words text-sm leading-relaxed text-text-muted">{failure.pattern}</p>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Detection (held-out)</div>
            <code className="code-panel mt-1.5 block p-3 font-mono text-[11px] leading-5 text-accent-muted">
              {failure.detectionRule}
            </code>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Failing held-out items</div>
            <ul className="mt-1.5 space-y-1 font-mono text-[11px] text-text-muted">
              {failure.heldOutItems.map((item) => (
                <li key={item} className="break-all">
                  • {item}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">
              Recommended harness change
            </div>
            <p className="mt-1.5 break-words text-sm leading-relaxed text-text-muted">
              {failure.recommendedHarnessChange}
            </p>
          </div>
        </div>

        <div className="border-t border-border-subtle p-4 font-mono text-[10px] leading-relaxed text-text-faint sm:p-5">
          Visible pass → held-out fail → failure shape → held-out coverage → re-eval
        </div>
      </aside>
    </div>
  );
}

export function FailureTaxonomySection() {
  const [failureId, setFailureId] = useState<string | null>(null);
  const selected = failureId ? heldOutFailures.find((f) => f.id === failureId) ?? null : null;

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
          title="What the held-out battery catches."
          description={
            <>
              The real shapes these runs exhibit at the baseline tier — missed malformed delimiters, a broken legacy
              caller, a narrowed parser, neighbouring latent defects. Each one clears the visible suite and only fails
              the held-out check; click a shape to inspect the failing items.
            </>
          }
          className="mb-8"
        />
        <div className="grid gap-3 md:grid-cols-2">
          {heldOutFailures.map((failure) => (
            <button
              key={failure.id}
              type="button"
              onClick={() => setFailureId(failure.id)}
              aria-label={`Inspect failure shape: ${failure.label}`}
              className="focus-ring group flex flex-col rounded-xl border border-border-subtle bg-surface/50 p-4 text-left transition-colors hover:bg-surface-2/60 sm:p-5"
            >
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-base font-medium text-text">{failure.label}</h3>
                <span className="shrink-0 rounded-md border border-border-subtle bg-surface-2 px-2 py-0.5 font-mono text-[10px] text-text-muted">
                  {failure.card.split(' · ')[0]}
                </span>
              </div>
              <p className="mt-1.5 flex-1 text-sm leading-relaxed text-text-muted">{failure.pattern}</p>
              <div className="mt-3 inline-flex items-center gap-1 text-xs text-accent-muted">
                Inspect shape
                <ChevronRight className="size-3 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
              </div>
            </button>
          ))}
        </div>
      </section>

      <HeldOutFailureDrawer failure={selected} open={selected !== null} onClose={() => setFailureId(null)} />
    </>
  );
}
