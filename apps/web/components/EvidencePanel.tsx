'use client';

import clsx from 'clsx';
import type { EvidenceTab, PolicyRun, TraceEvent } from '../lib/demoData';
import { buildFileTree, diffContent, stepHarnessNote, terminalContent } from '../lib/cockpitEvidence';
import { evidenceTabs } from '../lib/demoData';

type EvidencePanelProps = {
  run: PolicyRun;
  activeEvent: TraceEvent;
  tab: EvidenceTab;
  onTabChange: (tab: EvidenceTab) => void;
  knownFiles: string[];
};

function tabLabel(item: EvidenceTab) {
  return item;
}

export function EvidencePanel({ run, activeEvent, tab, onTabChange, knownFiles }: EvidencePanelProps) {
  const harnessNote = stepHarnessNote(activeEvent, run.name);

  return (
    <div className="surface-card p-3 sm:p-4">
      <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
        <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Evidence</div>
        <div className="font-mono text-[10px] text-text-faint">Step {String(activeEvent.step).padStart(2, '0')}</div>
      </div>

      <div className="mb-2.5 flex flex-wrap gap-1.5" role="tablist" aria-label="Evidence views">
        {evidenceTabs.map((item) => {
          const tabId = `evidence-tab-${item}`;
          const panelId = `evidence-panel-${item}`;
          return (
            <button
              key={item}
              id={tabId}
              type="button"
              role="tab"
              aria-selected={tab === item}
              aria-controls={panelId}
              onClick={() => onTabChange(item)}
              className={clsx(
                'focus-ring rounded-md px-2.5 py-1 font-mono text-[11px] capitalize',
                tab === item
                  ? 'bg-accent text-accent-foreground'
                  : 'border border-border-subtle text-text-muted hover:bg-surface-2'
              )}
            >
              {tabLabel(item)}
            </button>
          );
        })}
      </div>

      {harnessNote ? (
        <p className="mb-2.5 break-words rounded-md border border-warning/25 bg-warning/10 px-2.5 py-2 text-[11px] leading-5 text-warning">
          Harness note: {harnessNote}
        </p>
      ) : null}

      {evidenceTabs.map((item) => {
        const panelId = `evidence-panel-${item}`;
        const tabId = `evidence-tab-${item}`;
        const isActive = tab === item;

        return (
          <div
            key={item}
            id={panelId}
            role="tabpanel"
            aria-labelledby={tabId}
            hidden={!isActive}
            tabIndex={isActive ? 0 : -1}
          >
            {item === 'files' ? (
              <pre className="code-panel max-h-72 p-3 text-xs leading-6 sm:max-h-80">{buildFileTree(knownFiles, activeEvent.file)}</pre>
            ) : null}

            {item === 'terminal' ? (
              <pre className="code-panel min-h-28 max-h-72 p-3 text-xs leading-6 sm:min-h-32 sm:max-h-80">
                {terminalContent(activeEvent)}
              </pre>
            ) : null}

            {item === 'diff' ? (
              <pre className="code-panel min-h-28 max-h-72 p-3 text-xs leading-6 sm:min-h-32 sm:max-h-80">
                {diffContent(activeEvent)}
              </pre>
            ) : null}

            {item === 'judge' ? (
              <div className="space-y-2.5 text-sm leading-relaxed text-text-muted">
                <p className="break-words rounded-md border border-border-subtle bg-code-bg px-2.5 py-2 font-mono text-[10px] uppercase tracking-wide text-text-faint">
                  {run.verdict === 'rejected' ? 'Rejected' : run.verdict === 'assisted' ? 'Assisted' : 'Accepted'} ·{' '}
                  {run.primaryReason}
                </p>
                <ul className="space-y-1.5 text-xs">
                  {run.judgeNotes.map((note) => (
                    <li key={note} className="break-words">
                      • {note}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {item === 'raw' ? (
              <pre className="code-panel max-h-80 p-3 text-xs leading-6">{JSON.stringify(activeEvent, null, 2)}</pre>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
