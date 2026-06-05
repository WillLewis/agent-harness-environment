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
    <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-4 sm:p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Evidence</div>
        <div className="font-mono text-[11px] text-slate-500">Step {String(activeEvent.step).padStart(2, '0')}</div>
      </div>

      <div className="mb-3 flex flex-wrap gap-2" role="tablist" aria-label="Evidence views">
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
                'focus-ring rounded-full px-3 py-1.5 text-xs capitalize',
                tab === item ? 'bg-cyan-300 text-slate-950' : 'border border-white/10 text-slate-300'
              )}
            >
              {tabLabel(item)}
            </button>
          );
        })}
      </div>

      {harnessNote ? (
        <p className="mb-3 break-words rounded-2xl border border-amber-300/20 bg-amber-300/5 px-3 py-2 text-xs leading-5 text-amber-100">
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
              <pre className="code-panel max-h-72 rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300 sm:max-h-80">
                {buildFileTree(knownFiles, activeEvent.file)}
              </pre>
            ) : null}

            {item === 'terminal' ? (
              <pre className="code-panel min-h-32 max-h-72 rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300 sm:min-h-40 sm:max-h-80">
                {terminalContent(activeEvent)}
              </pre>
            ) : null}

            {item === 'diff' ? (
              <pre className="code-panel min-h-32 max-h-72 rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300 sm:min-h-40 sm:max-h-80">
                {diffContent(activeEvent)}
              </pre>
            ) : null}

            {item === 'judge' ? (
              <div className="space-y-3 text-sm leading-6 text-slate-300">
                <p className="break-words rounded-2xl border border-white/10 bg-black/20 px-3 py-2 text-xs uppercase tracking-[0.18em] text-slate-400">
                  {run.verdict === 'rejected' ? 'Rejected' : run.verdict === 'assisted' ? 'Assisted' : 'Accepted'} ·{' '}
                  {run.primaryReason}
                </p>
                <ul className="space-y-2">
                  {run.judgeNotes.map((note) => (
                    <li key={note} className="break-words">
                      • {note}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {item === 'raw' ? (
              <pre className="code-panel max-h-80 rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">
                {JSON.stringify(activeEvent, null, 2)}
              </pre>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
