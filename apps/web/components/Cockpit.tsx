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
import { selectableActiveClass, selectableIdleClass } from '../lib/statusStyles';

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
    <section id="cockpit" className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8" aria-label="Interactive cockpit">
      <div className="mb-5 flex flex-col justify-between gap-3 lg:flex-row lg:items-end">
        <div>
          <p className="section-chapter">
            <span className="text-accent-muted">04</span>
            <span className="mx-2 text-border">—</span>
            <span className="section-label">Interactive cockpit</span>
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-text sm:text-3xl">
            Same task. Different harness. Different outcome.
          </h2>
        </div>
        <p className="max-w-2xl text-xs leading-relaxed text-text-muted sm:text-sm">
          Precomputed fixtures from <span className="font-mono text-text-muted">data/traces/</span>. Select task and
          policy to replay trace, metrics, evidence, and verdict together — no network requests.
        </p>
      </div>

      <div className="grid min-w-0 grid-cols-1 gap-3 lg:grid-cols-[minmax(0,280px)_minmax(0,1fr)_minmax(0,320px)]">
        <aside className="surface-card min-w-0 p-3 sm:p-4">
          <div className="rounded-lg border border-accent/30 bg-accent-subtle p-3">
            <div className="font-mono text-[10px] font-semibold uppercase tracking-wider text-accent-muted">{task.label}</div>
            <h3 className="mt-1.5 text-base font-semibold text-text">{task.title}</h3>
            <p className="mt-2 text-xs leading-relaxed text-text-muted">{task.issue}</p>
            <div className="code-panel mt-3 break-all p-2.5 font-mono text-[11px]">{task.successCommand}</div>
          </div>

          <div className="mt-4">
            <div id="cockpit-task-label" className="font-mono text-[10px] uppercase tracking-wider text-text-faint">
              Task
            </div>
            <div
              className="mt-2 space-y-1.5"
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
                      'focus-ring w-full rounded-lg border p-2.5 text-left transition',
                      id === taskId ? selectableActiveClass : selectableIdleClass
                    )}
                  >
                    <div className="text-sm font-semibold text-text">{option.label}</div>
                    <p className="mt-0.5 text-[11px] leading-4 text-text-faint">{option.title}</p>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-4">
            <div id="cockpit-policy-label" className="font-mono text-[10px] uppercase tracking-wider text-text-faint">
              Policy
            </div>
            <div className="mt-2 space-y-1.5" role="group" aria-labelledby="cockpit-policy-label">
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
                      'focus-ring w-full rounded-lg border p-2.5 text-left transition',
                      id === policyId ? selectableActiveClass : selectableIdleClass
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="text-sm font-semibold text-text">{policyRun.name}</div>
                      <span className="font-mono text-[10px] text-text-faint">{index + 1}</span>
                    </div>
                    <p className="mt-0.5 text-[11px] leading-4 text-text-faint">{policyRun.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-4">
            <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Failure modes to watch</div>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {task.failureModes.map((mode) => (
                <span
                  key={mode}
                  className="rounded border border-border-subtle px-1.5 py-0.5 font-mono text-[10px] text-text-muted"
                >
                  {mode}
                </span>
              ))}
            </div>
          </div>

          <p id="cockpit-task-hint" className="mt-4 text-[10px] leading-4 text-text-faint">
            Keyboard: <span className="font-mono">[ ]</span> tasks ·{' '}
            <span className="font-mono">1-{task.policyOrder.length}</span> policies ·{' '}
            <span className="font-mono">← →</span> steps · <span className="font-mono">f t d j r</span> evidence tabs
          </p>
        </aside>

        <main className="surface-card min-w-0 p-3 sm:p-4">
          <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Trace replay</div>
              <h3 className="mt-0.5 text-base font-semibold text-text">{run.name}</h3>
              <p className="mt-0.5 font-mono text-[10px] text-text-faint">
                {task.label} · {run.events.length} steps · {run.verdict} verdict
              </p>
            </div>
            <div className="flex shrink-0 gap-1.5">
              <button
                type="button"
                className="focus-ring rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[11px] text-text-muted hover:bg-surface-2"
                onClick={() => selectStep(activeStep - 1)}
                aria-label="Previous trace step"
              >
                Back
              </button>
              <button
                type="button"
                className="focus-ring rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[11px] text-text-muted hover:bg-surface-2"
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
            <div className="max-h-[min(70vh,720px)] overflow-y-auto pr-0.5 lg:max-h-none lg:overflow-visible">
              <TraceTimeline events={run.events} activeStep={activeStep} onSelect={selectStep} policyName={run.name} />
            </div>
          </motion.div>
        </main>

        <aside className="min-w-0 space-y-3">
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
            className="grid grid-cols-2 gap-2"
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
