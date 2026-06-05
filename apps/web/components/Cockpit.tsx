'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import { motion, useReducedMotion } from 'framer-motion';
import { MetricCard } from './MetricCard';
import { TraceTimeline } from './TraceTimeline';
import { EvidencePanel } from './EvidencePanel';
import { VerdictStamp } from './VerdictStamp';
import { defaultTabForPolicy, findEvent, tabForEvent } from '../lib/cockpitEvidence';
import { demoTask, policyRuns, type EvidenceTab, type PolicyId } from '../lib/demoData';

const policyOrder: PolicyId[] = ['baseline', 'guarded_recovery', 'baseline_with_steering'];

function verdictLabel(verdict: string) {
  if (verdict === 'accepted') return 'ACCEPTED BY JUDGE';
  if (verdict === 'assisted') return 'ACCEPTED WITH STEERING';
  return 'REJECTED BY JUDGE';
}

function formatMetric(value: number) {
  return Number.isInteger(value) ? value : value.toFixed(2);
}

export function Cockpit() {
  const reduceMotion = useReducedMotion();
  const [policyId, setPolicyId] = useState<PolicyId>('baseline');
  const [activeStep, setActiveStep] = useState(1);
  const [tab, setTab] = useState<EvidenceTab>('terminal');
  const run = policyRuns[policyId];
  const activeEvent = useMemo(() => findEvent(run.events, activeStep), [run.events, activeStep]);

  const selectPolicy = useCallback((next: PolicyId) => {
    setPolicyId(next);
    setActiveStep(1);
    const firstEvent = policyRuns[next].events[0];
    setTab(firstEvent ? tabForEvent(firstEvent) : defaultTabForPolicy(next));
  }, []);

  const selectStep = useCallback(
    (step: number) => {
      const clamped = Math.max(1, Math.min(run.events.length, step));
      const event = findEvent(run.events, clamped);
      setActiveStep(clamped);
      setTab(tabForEvent(event));
    },
    [run.events]
  );

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.closest('input, textarea, select, [contenteditable="true"]')) return;

      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        selectStep(activeStep - 1);
        return;
      }
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        selectStep(activeStep + 1);
        return;
      }
      if (event.key === '1') {
        event.preventDefault();
        selectPolicy('baseline');
        return;
      }
      if (event.key === '2') {
        event.preventDefault();
        selectPolicy('guarded_recovery');
        return;
      }
      if (event.key === '3') {
        event.preventDefault();
        selectPolicy('baseline_with_steering');
        return;
      }
      const tabKeys: Record<string, EvidenceTab> = {
        f: 'files',
        t: 'terminal',
        d: 'diff',
        j: 'judge',
        r: 'raw'
      };
      const nextTab = tabKeys[event.key.toLowerCase()];
      if (nextTab) {
        event.preventDefault();
        setTab(nextTab);
      }
    }

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [activeStep, selectPolicy, selectStep]);

  return (
    <section id="cockpit" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8" aria-label="Interactive cockpit">
      <div className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Interactive cockpit</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">Same task. Different harness. Different outcome.</h2>
        </div>
        <p className="max-w-2xl text-sm leading-6 text-slate-400">
          Hosted demo uses precomputed traces. Toggle policy to replay trace, metrics, evidence, and verdict together.
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
            <div className="mt-3 space-y-2" role="group" aria-label="Harness policy">
              {policyOrder.map((id, index) => (
                <button
                  key={id}
                  type="button"
                  aria-pressed={id === policyId}
                  onClick={() => selectPolicy(id)}
                  className={clsx(
                    'focus-ring w-full rounded-2xl border p-3 text-left transition',
                    id === policyId ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.06]'
                  )}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="font-semibold text-white">{policyRuns[id].name}</div>
                    <span className="font-mono text-[10px] text-slate-500">{index + 1}</span>
                  </div>
                  <p className="mt-1 text-xs leading-5 text-slate-400">{policyRuns[id].description}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-5">
            <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Failure modes to watch</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {demoTask.failureModes.map((mode) => (
                <span key={mode} className="rounded-full border border-white/10 px-2 py-1 font-mono text-[11px] text-slate-300">
                  {mode}
                </span>
              ))}
            </div>
          </div>

          <p className="mt-5 text-[11px] leading-5 text-slate-500">
            Keyboard: <span className="font-mono">1-3</span> policies · <span className="font-mono">← →</span> steps ·{' '}
            <span className="font-mono">f t d j r</span> evidence tabs
          </p>
        </aside>

        <main className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Trace replay</div>
              <h3 className="mt-1 text-xl font-semibold text-white">{run.name}</h3>
              <p className="mt-1 text-xs text-slate-500">{run.events.length} steps · {run.verdict} verdict</p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                className="focus-ring rounded-full border border-white/10 px-3 py-2 text-xs text-slate-300"
                onClick={() => selectStep(activeStep - 1)}
                aria-label="Previous trace step"
              >
                Back
              </button>
              <button
                type="button"
                className="focus-ring rounded-full border border-white/10 px-3 py-2 text-xs text-slate-300"
                onClick={() => selectStep(activeStep + 1)}
                aria-label="Next trace step"
              >
                Step
              </button>
            </div>
          </div>
          <motion.div
            key={policyId}
            initial={reduceMotion ? false : { opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: reduceMotion ? 0 : 0.25 }}
          >
            <TraceTimeline events={run.events} activeStep={activeStep} onSelect={selectStep} policyName={run.name} />
          </motion.div>
        </main>

        <aside className="space-y-4">
          <VerdictStamp
            policyKey={policyId}
            verdict={run.verdict}
            label={verdictLabel(run.verdict)}
            reason={run.primaryReason}
          />

          <motion.div
            key={policyId}
            initial={reduceMotion ? false : { opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: reduceMotion ? 0 : 0.25, delay: reduceMotion ? 0 : 0.05 }}
            className="grid grid-cols-2 gap-3"
            aria-live="polite"
            aria-label="Eval metrics"
          >
            <MetricCard label="task_success" value={formatMetric(run.metrics.taskSuccess)} />
            <MetricCard label="recovery" value={formatMetric(run.metrics.recoveryScore)} />
            <MetricCard label="loop" value={formatMetric(run.metrics.loopScore)} />
            <MetricCard label="human" value={formatMetric(run.metrics.humanInterventions)} />
          </motion.div>

          <EvidencePanel run={run} activeEvent={activeEvent} tab={tab} onTabChange={setTab} />
        </aside>
      </div>
    </section>
  );
}
