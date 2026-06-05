'use client';

import clsx from 'clsx';
import type { EvidenceTab, PolicyRun, TraceEvent } from '../lib/demoData';
import { buildFileTree, diffContent, stepHarnessNote, terminalContent } from '../lib/cockpitEvidence';
import { demoTask, evidenceTabs } from '../lib/demoData';

type EvidencePanelProps = {
  run: PolicyRun;
  activeEvent: TraceEvent;
  tab: EvidenceTab;
  onTabChange: (tab: EvidenceTab) => void;
};

export function EvidencePanel({ run, activeEvent, tab, onTabChange }: EvidencePanelProps) {
  const harnessNote = stepHarnessNote(activeEvent, run.name);

  return (
    <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Evidence</div>
        <div className="font-mono text-[11px] text-slate-500">Step {String(activeEvent.step).padStart(2, '0')}</div>
      </div>

      <div className="mb-3 flex flex-wrap gap-2" role="tablist" aria-label="Evidence panels">
        {evidenceTabs.map((item) => (
          <button
            key={item}
            type="button"
            role="tab"
            aria-selected={tab === item}
            onClick={() => onTabChange(item)}
            className={clsx(
              'focus-ring rounded-full px-3 py-1.5 text-xs capitalize',
              tab === item ? 'bg-cyan-300 text-slate-950' : 'border border-white/10 text-slate-300'
            )}
          >
            {item}
          </button>
        ))}
      </div>

      {harnessNote ? (
        <p className="mb-3 rounded-2xl border border-amber-300/20 bg-amber-300/5 px-3 py-2 text-xs leading-5 text-amber-100">
          Harness note: {harnessNote}
        </p>
      ) : null}

      {tab === 'files' ? (
        <pre className="overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">
          {buildFileTree(demoTask.knownFiles, activeEvent.file)}
        </pre>
      ) : null}

      {tab === 'terminal' ? (
        <pre className="min-h-40 overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">
          {terminalContent(activeEvent)}
        </pre>
      ) : null}

      {tab === 'diff' ? (
        <pre className="min-h-40 overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">
          {diffContent(activeEvent)}
        </pre>
      ) : null}

      {tab === 'judge' ? (
        <div className="space-y-3 text-sm leading-6 text-slate-300">
          <p className="rounded-2xl border border-white/10 bg-black/20 px-3 py-2 text-xs uppercase tracking-[0.18em] text-slate-400">
            {run.verdict === 'rejected' ? 'Rejected' : run.verdict === 'assisted' ? 'Assisted' : 'Accepted'} · {run.primaryReason}
          </p>
          <ul className="space-y-2">
            {run.judgeNotes.map((note) => (
              <li key={note}>• {note}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {tab === 'raw' ? (
        <pre className="max-h-80 overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">
          {JSON.stringify(activeEvent, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
