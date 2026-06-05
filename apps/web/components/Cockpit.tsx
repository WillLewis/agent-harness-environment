'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import { motion, useReducedMotion } from 'framer-motion';
import { MetricCard } from './MetricCard';
import { TraceTimeline } from './TraceTimeline';
import { EvidencePanel } from './EvidencePanel';
import { VerdictStamp } from './VerdictStamp';
import { defaultTabForRun, findEvent, tabForEvent } from '../lib/cockpitEvidence';
import {
  cockpitTaskOrder,
  DEFAULT_TASK_ID,
  getCockpitTask,
  type EvidenceTab,
  type PolicyId,
  type TaskId
} from '../lib/demoData';

function verdictLabel(verdict: string) {
  if (verdict === 'accepted') return 'ACCEPTED BY JUDGE';
  if (verdict === 'assisted') return 'ACCEPTED WITH STEERING';
  return 'REJECTED BY JUDGE';
}

function formatMetric(value: number) {
  return Number.isInteger(value) ? value : value.toFixed(2);
}

function resolvePolicyRun(taskId: TaskId, policyId: PolicyId) {
  const task = getCockpitTask(taskId);
  const run = task.policies[policyId];
  if (!run) {
    const fallback = task.policyOrder[0];
    return task.policies[fallback]!;
  }
  return run;
}

export function Cockpit() {
  const reduceMotion = useReducedMotion();
  const [taskId, setTaskId] = useState<TaskId>(DEFAULT_TASK_ID);
  const [policyId, setPolicyId] = useState<PolicyId>('baseline');
  const [activeStep, setActiveStep] = useState(1);
  const [tab, setTab] = useState<EvidenceTab>('terminal');

  const task = getCockpitTask(taskId);
  const run = resolvePolicyRun(taskId, policyId);
  const activeEvent = useMemo(() => findEvent(run.events, activeStep), [run.events, activeStep]);

  const selectTask = useCallback((nextTaskId: TaskId) => {
    const nextTask = getCockpitTask(nextTaskId);
    const nextPolicy = nextTask.defaultPolicyId;
    const nextRun = nextTask.policies[nextPolicy]!;
    setTaskId(nextTaskId);
    setPolicyId(nextPolicy);
    setActiveStep(1);
    const firstEvent = nextRun.events[0];
    setTab(
      firstEvent
        ? tabForEvent(firstEvent)
        : defaultTabForRun(nextPolicy, nextTaskId, nextRun.events)
    );
  }, []);

  const selectPolicy = useCallback(
    (next: PolicyId) => {
      const nextRun = resolvePolicyRun(taskId, next);
      setPolicyId(next);
      setActiveStep(1);
      const firstEvent = nextRun.events[0];
      setTab(
        firstEvent
          ? tabForEvent(firstEvent)
          : defaultTabForRun(next, taskId, nextRun.events)
      );
    },
    [taskId]
  );

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

      const taskIndex = cockpitTaskOrder.indexOf(taskId);
      if (event.key === '[' && taskIndex > 0) {
        event.preventDefault();
        selectTask(cockpitTaskOrder[taskIndex - 1]);
        return;
      }
      if (event.key === ']' && taskIndex < cockpitTaskOrder.length - 1) {
        event.preventDefault();
        selectTask(cockpitTaskOrder[taskIndex + 1]);
        return;
      }

      const policyIndex = Number(event.key) - 1;
      if (policyIndex >= 0 && policyIndex < task.policyOrder.length) {
        event.preventDefault();
        selectPolicy(task.policyOrder[policyIndex]);
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
  }, [activeStep, selectPolicy, selectStep, selectTask, task.policyOrder, taskId]);

  const replayKey = `${taskId}-${policyId}`;

  return (
    <section id="cockpit" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8" aria-label="Interactive cockpit">
      <div className="mb-6 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Interactive cockpit</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Same task. Different harness. Different outcome.
          </h2>
        </div>
        <p className="max-w-2xl text-sm leading-6 text-slate-400">
          Precomputed fixtures from <span className="font-mono text-slate-300">data/traces/</span>. Select task and
          policy to replay trace, metrics, evidence, and verdict together — no network requests.
        </p>
      </div>

      <div className="grid min-w-0 grid-cols-1 gap-4 lg:grid-cols-[minmax(0,300px)_minmax(0,1fr)_minmax(0,340px)]">
        <aside className="min-w-0 rounded-3xl border border-white/10 bg-white/[0.03] p-4 sm:p-5">
          <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-4">
            <div className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-100">{task.label}</div>
            <h3 className="mt-2 text-xl font-semibold text-white">{task.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">{task.issue}</p>
            <div className="mt-4 break-all rounded-xl bg-black/30 p-3 font-mono text-xs text-slate-300">
              {task.successCommand}
            </div>
          </div>

          <div className="mt-5">
            <div id="cockpit-task-label" className="text-xs uppercase tracking-[0.22em] text-slate-500">
              Task
            </div>
            <div
              className="mt-3 space-y-2"
              role="group"
              aria-labelledby="cockpit-task-label"
              aria-describedby="cockpit-task-hint"
            >
              {cockpitTaskOrder.map((id) => {
                const option = getCockpitTask(id);
                return (
                  <button
                    key={id}
                    type="button"
                    aria-pressed={id === taskId}
                    aria-label={`${option.label}: ${option.title}`}
                    onClick={() => selectTask(id)}
                    className={clsx(
                      'focus-ring w-full rounded-2xl border p-3 text-left transition',
                      id === taskId
                        ? 'border-cyan-300/60 bg-cyan-300/10'
                        : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.06]'
                    )}
                  >
                    <div className="font-semibold text-white">{option.label}</div>
                    <p className="mt-1 text-xs leading-5 text-slate-400">{option.title}</p>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-5">
            <div id="cockpit-policy-label" className="text-xs uppercase tracking-[0.22em] text-slate-500">
              Policy
            </div>
            <div className="mt-3 space-y-2" role="group" aria-labelledby="cockpit-policy-label">
              {task.policyOrder.map((id, index) => {
                const policyRun = task.policies[id];
                if (!policyRun) return null;
                return (
                  <button
                    key={id}
                    type="button"
                    aria-pressed={id === policyId}
                    aria-label={`${policyRun.name}. ${policyRun.description}`}
                    onClick={() => selectPolicy(id)}
                    className={clsx(
                      'focus-ring w-full rounded-2xl border p-3 text-left transition',
                      id === policyId
                        ? 'border-cyan-300/60 bg-cyan-300/10'
                        : 'border-white/10 bg-white/[0.03] hover:bg-white/[0.06]'
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="font-semibold text-white">{policyRun.name}</div>
                      <span className="font-mono text-[10px] text-slate-500">{index + 1}</span>
                    </div>
                    <p className="mt-1 text-xs leading-5 text-slate-400">{policyRun.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-5">
            <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Failure modes to watch</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {task.failureModes.map((mode) => (
                <span key={mode} className="rounded-full border border-white/10 px-2 py-1 font-mono text-[11px] text-slate-300">
                  {mode}
                </span>
              ))}
            </div>
          </div>

          <p id="cockpit-task-hint" className="mt-5 text-[11px] leading-5 text-slate-500">
            Keyboard: <span className="font-mono">[ ]</span> tasks ·{' '}
            <span className="font-mono">1-{task.policyOrder.length}</span> policies ·{' '}
            <span className="font-mono">← →</span> steps · <span className="font-mono">f t d j r</span> evidence tabs
          </p>
        </aside>

        <main className="min-w-0 rounded-3xl border border-white/10 bg-white/[0.03] p-4 sm:p-5">
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.22em] text-slate-500">Trace replay</div>
              <h3 className="mt-1 text-xl font-semibold text-white">{run.name}</h3>
              <p className="mt-1 text-xs text-slate-500">
                {task.label} · {run.events.length} steps · {run.verdict} verdict
              </p>
            </div>
            <div className="flex shrink-0 gap-2">
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
            key={replayKey}
            initial={reduceMotion ? false : { opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: reduceMotion ? 0 : 0.25 }}
          >
            <div className="max-h-[min(70vh,720px)] overflow-y-auto pr-1 lg:max-h-none lg:overflow-visible">
              <TraceTimeline events={run.events} activeStep={activeStep} onSelect={selectStep} policyName={run.name} />
            </div>
          </motion.div>
        </main>

        <aside className="min-w-0 space-y-4">
          <VerdictStamp
            policyKey={`${taskId}-${policyId}`}
            verdict={run.verdict}
            label={verdictLabel(run.verdict)}
            reason={run.primaryReason}
          />

          <motion.div
            key={replayKey}
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
            <MetricCard
              label={taskId === 'adversarial_env_001' ? 'unsafe' : 'human'}
              value={formatMetric(
                taskId === 'adversarial_env_001' ? run.metrics.unsafeAttempts : run.metrics.humanInterventions
              )}
            />
          </motion.div>

          <EvidencePanel
            run={run}
            activeEvent={activeEvent}
            tab={tab}
            onTabChange={setTab}
            knownFiles={task.knownFiles}
          />
        </aside>
      </div>
    </section>
  );
}
