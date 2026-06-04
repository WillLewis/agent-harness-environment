'use client';

import { useMemo, useState } from 'react';
import clsx from 'clsx';
import { MetricCard } from './MetricCard';
import { TraceTimeline } from './TraceTimeline';
import { demoTask, policyRuns, type PolicyId } from '../lib/demoData';

const policyOrder: PolicyId[] = ['baseline', 'guarded_recovery', 'baseline_with_steering'];
const evidenceTabs = ['files', 'terminal', 'diff', 'judge', 'raw'] as const;
type EvidenceTab = (typeof evidenceTabs)[number];

function verdictLabel(verdict: string) {
  if (verdict === 'accepted') return 'ACCEPTED BY JUDGE';
  if (verdict === 'assisted') return 'ACCEPTED WITH STEERING';
  return 'REJECTED BY JUDGE';
}

export function Cockpit() {
  const [policyId, setPolicyId] = useState<PolicyId>('baseline');
  const [activeStep, setActiveStep] = useState(1);
  const [tab, setTab] = useState<EvidenceTab>('terminal');
  const run = policyRuns[policyId];
  const activeEvent = useMemo(() => run.events.find((event) => event.step === activeStep) ?? run.events[0], [run.events, activeStep]);

  function selectPolicy(next: PolicyId) {
    setPolicyId(next);
    setActiveStep(1);
    setTab(next === 'guarded_recovery' ? 'judge' : 'terminal');
  }

  return (
    <section id="cockpit" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Interactive cockpit</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">Same task. Different harness. Different outcome.</h2>
        </div>
        <p className="max-w-2xl text-sm leading-6 text-slate-400">
          Hosted demo uses precomputed traces. The local repo includes starter runner, scorer, and MCP surfaces for fresh traces.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[300px_minmax(0,1fr)_340px]">
        <aside className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-4">
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-100">{demoTask.label}</div>
            <h3 className="mt-2 text-xl font-semibold text-white">{demoTask.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">{demoTask.issue}</p>
            <div className="mt-4 rounded-xl bg-black/30 p-3 font-mono text-xs text-slate-300">{demoTask.successCommand}</div>
          </div>

          <div className="mt-5">
            <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Policy</div>
            <div className="mt-3 space-y-2">
              {policyOrder.map((id) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => selectPolicy(id)}
                  className={clsx(
                    'focus-ring w-full rounded-2xl border p-3 text-left transition',
                    id === policyId ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.06]'
                  )}
                >
                  <div className="font-semibold text-white">{policyRuns[id].name}</div>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{policyRuns[id].description}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5">
            <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Failure modes to watch</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {demoTask.failureModes.map((mode) => (
                <span key={mode} className="rounded-full border border-white/10 px-2 py-1 font-mono text-[11px] text-slate-300">{mode}</span>
              ))}
            </div>
          </div>
        </aside>

        <main className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Trace replay</div>
              <h3 className="mt-1 text-xl font-semibold text-white">{run.name}</h3>
            </div>
            <div className="flex gap-2">
              <button className="focus-ring rounded-full border border-white/10 px-3 py-2 text-xs text-slate-300" onClick={() => setActiveStep(Math.max(1, activeStep - 1))}>Back</button>
              <button className="focus-ring rounded-full border border-white/10 px-3 py-2 text-xs text-slate-300" onClick={() => setActiveStep(Math.min(run.events.length, activeStep + 1))}>Step</button>
            </div>
          </div>
          <TraceTimeline events={run.events} activeStep={activeStep} onSelect={setActiveStep} />
        </main>

        <aside className="space-y-4">
          <div className={clsx('rounded-3xl border p-5', run.verdict === 'rejected' ? 'border-red-300/30 bg-red-300/10' : 'border-emerald-300/30 bg-emerald-300/10')}>
            <div className="text-xs uppercase tracking-[0.28em] text-slate-300">Verdict</div>
            <div className="mt-2 text-2xl font-black tracking-tight text-white">{verdictLabel(run.verdict)}</div>
            <p className="mt-3 text-sm leading-6 text-slate-200">{run.primaryReason}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <MetricCard label="task_success" value={run.metrics.taskSuccess} />
            <MetricCard label="recovery" value={run.metrics.recoveryScore} />
            <MetricCard label="loop" value={run.metrics.loopScore} />
            <MetricCard label="human" value={run.metrics.humanInterventions} />
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <div className="mb-3 flex flex-wrap gap-2">
              {evidenceTabs.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setTab(item)}
                  className={clsx('focus-ring rounded-full px-3 py-1.5 text-xs capitalize', tab === item ? 'bg-cyan-300 text-slate-950' : 'border border-white/10 text-slate-300')}
                >
                  {item}
                </button>
              ))}
            </div>

            {tab === 'files' ? (
              <pre className="overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">{`toy-repo/\n  src/\n    dateParser.ts ${activeEvent.file === 'src/dateParser.ts' ? '← active' : ''}\n  tests/\n    dateParser.test.ts ${activeEvent.file === 'tests/dateParser.test.ts' ? '← active' : ''}\n  package.json`}</pre>
            ) : null}
            {tab === 'terminal' ? (
              <pre className="min-h-40 overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">{activeEvent.terminalOutput ?? activeEvent.command ?? 'No terminal output for this step.'}</pre>
            ) : null}
            {tab === 'diff' ? (
              <pre className="min-h-40 overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">{activeEvent.diff ?? 'No diff for this step.'}</pre>
            ) : null}
            {tab === 'judge' ? (
              <ul className="space-y-2 text-sm leading-6 text-slate-300">
                {run.judgeNotes.map((note) => <li key={note}>• {note}</li>)}
              </ul>
            ) : null}
            {tab === 'raw' ? (
              <pre className="max-h-80 overflow-auto rounded-2xl bg-black/40 p-4 text-xs leading-6 text-slate-300">{JSON.stringify(activeEvent, null, 2)}</pre>
            ) : null}
          </div>
        </aside>
      </div>
    </section>
  );
}
