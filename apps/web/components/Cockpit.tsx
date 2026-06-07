'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import clsx from 'clsx';
import { motion, useReducedMotion } from 'framer-motion';
import { Pause, Play, RotateCcw, SkipBack, SkipForward, GitBranch } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { TraceTimeline } from './TraceTimeline';
import { EvidencePanel } from './EvidencePanel';
import { VerdictStamp } from './VerdictStamp';
import { ObservabilityLinks } from './ObservabilityLinks';
import { defaultTabForRun, findEvent, tabForEvent } from '../lib/cockpitEvidence';
import {
  cockpitTaskOrder,
  DEFAULT_TASK_ID,
  getCockpitTask,
  type EvidenceTab,
  type PolicyId,
  type TaskId,
  type TraceEvent
} from '../lib/demoData';
import { selectableActiveClass, selectableIdleClass } from '../lib/statusStyles';

type CockpitProps = {
  activeTaskId: TaskId;
  onTaskChange: (taskId: TaskId) => void;
  autoplayToken: number;
};

type CockpitPolicyId = PolicyId;

const basePolicyOptionOrder: CockpitPolicyId[] = [
  'baseline',
  'test_first',
  'context_first',
  'guarded_recovery'
];

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

function isReplayPolicyId(policyId: string): policyId is PolicyId {
  return (
    policyId === 'baseline' ||
    policyId === 'test_first' ||
    policyId === 'context_first' ||
    policyId === 'guarded_recovery' ||
    policyId === 'baseline_with_steering' ||
    policyId === 'gamed_attempt'
  );
}

function policyOptionOrder(taskId: TaskId): CockpitPolicyId[] {
  const task = getCockpitTask(taskId);
  if (task.policies.baseline_with_steering) {
    return [
      'baseline',
      'test_first',
      'context_first',
      'guarded_recovery',
      'baseline_with_steering',
      'gamed_attempt'
    ];
  }
  return basePolicyOptionOrder;
}

function replayPolicyForOption(taskId: TaskId, policyOptionId: CockpitPolicyId): PolicyId {
  const task = getCockpitTask(taskId);
  if (isReplayPolicyId(policyOptionId) && task.policies[policyOptionId]) {
    return policyOptionId;
  }
  return task.policies.guarded_recovery ? 'guarded_recovery' : 'baseline';
}

function policyDisplayName(policyId: string): string {
  if (policyId === 'baseline') return 'Baseline';
  if (policyId === 'test_first') return 'Test-first';
  if (policyId === 'context_first') return 'Context-first';
  if (policyId === 'guarded_recovery') return 'Guarded recovery';
  if (policyId === 'baseline_with_steering') return 'Baseline with steering';
  if (policyId === 'gamed_attempt') return 'Gamed (edits the test)';
  return policyId.replace(/_/g, ' ');
}

function policyOptionMeta(taskId: TaskId, policyOptionId: CockpitPolicyId) {
  const run = getCockpitTask(taskId).policies[policyOptionId];
  return run
    ? { name: run.name, description: run.description, badge: null }
    : { name: policyDisplayName(policyOptionId), description: '', badge: null };
}

function firstTabForRun(taskId: TaskId, policyId: PolicyId) {
  const task = getCockpitTask(taskId);
  const run = resolvePolicyRun(taskId, policyId);
  const firstEvent = run.events[0];
  return firstEvent ? tabForEvent(firstEvent) : defaultTabForRun(policyId, taskId, run.events);
}

export function Cockpit({ activeTaskId, onTaskChange, autoplayToken }: CockpitProps) {
  const reduceMotion = useReducedMotion();
  const [policyOptionId, setPolicyOptionId] = useState<CockpitPolicyId>('baseline');
  const [activeStep, setActiveStep] = useState(1);
  const [tab, setTab] = useState<EvidenceTab>('terminal');
  const [playing, setPlaying] = useState(false);
  const [steeringDeclined, setSteeringDeclined] = useState(false);
  const timerRef = useRef<number | null>(null);

  const task = getCockpitTask(activeTaskId);
  const options = useMemo(() => policyOptionOrder(activeTaskId), [activeTaskId]);
  const replayPolicyId = replayPolicyForOption(activeTaskId, policyOptionId);
  const run = resolvePolicyRun(activeTaskId, replayPolicyId);
  const activeEvent = useMemo(() => findEvent(run.events, activeStep), [run.events, activeStep]);
  const replayKey = `${activeTaskId}-${policyOptionId}-${replayPolicyId}`;
  const loopSteeringAvailable =
    activeTaskId === DEFAULT_TASK_ID &&
    policyOptionId === 'baseline' &&
    activeEvent?.label === 'loop_detected' &&
    !steeringDeclined;

  const setStepAndTab = useCallback(
    (step: number, options?: { keepPlaying?: boolean }) => {
      const clamped = Math.max(1, Math.min(run.events.length, step));
      const event = findEvent(run.events, clamped);
      setActiveStep(clamped);
      setTab(tabForEvent(event));
      if (!options?.keepPlaying) {
        setPlaying(false);
      }
    },
    [run.events]
  );

  const selectTask = useCallback(
    (nextTaskId: TaskId) => {
      onTaskChange(nextTaskId);
    },
    [onTaskChange]
  );

  const selectPolicy = useCallback(
    (next: CockpitPolicyId, nextOptions?: { autoplay?: boolean }) => {
      const nextReplayPolicy = replayPolicyForOption(activeTaskId, next);
      const nextRun = resolvePolicyRun(activeTaskId, nextReplayPolicy);
      const firstEvent = nextRun.events[0];
      setPolicyOptionId(next);
      setActiveStep(1);
      setSteeringDeclined(false);
      setTab(
        firstEvent
          ? tabForEvent(firstEvent)
          : defaultTabForRun(nextReplayPolicy, activeTaskId, nextRun.events)
      );
      setPlaying(Boolean(nextOptions?.autoplay));
    },
    [activeTaskId]
  );

  const resetReplay = useCallback(() => {
    setActiveStep(1);
    setSteeringDeclined(false);
    setPlaying(false);
    setTab(firstTabForRun(activeTaskId, replayPolicyId));
  }, [activeTaskId, replayPolicyId]);

  useEffect(() => {
    const defaultPolicy = getCockpitTask(activeTaskId).defaultPolicyId;
    setPolicyOptionId(defaultPolicy);
    setActiveStep(1);
    setSteeringDeclined(false);
    setPlaying(false);
    setTab(firstTabForRun(activeTaskId, defaultPolicy));
  }, [activeTaskId]);

  useEffect(() => {
    if (autoplayToken <= 0) return;
    setPolicyOptionId('baseline');
    setActiveStep(1);
    setSteeringDeclined(false);
    setTab(firstTabForRun(activeTaskId, 'baseline'));
    setPlaying(true);
  }, [activeTaskId, autoplayToken]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.closest('input, textarea, select, [contenteditable="true"]')) return;

      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        setStepAndTab(activeStep - 1);
        return;
      }
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        setStepAndTab(activeStep + 1);
        return;
      }

      const taskIndex = cockpitTaskOrder.indexOf(activeTaskId);
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
      if (policyIndex >= 0 && policyIndex < options.length) {
        event.preventDefault();
        selectPolicy(options[policyIndex]);
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
  }, [activeStep, activeTaskId, options, selectPolicy, selectTask, setStepAndTab]);

  useEffect(() => {
    if (!playing) return;
    if (loopSteeringAvailable || activeStep >= run.events.length) {
      setPlaying(false);
      return;
    }
    timerRef.current = window.setTimeout(() => {
      setStepAndTab(activeStep + 1, { keepPlaying: true });
    }, 900);
    return () => {
      if (timerRef.current) {
        window.clearTimeout(timerRef.current);
      }
    };
  }, [activeStep, loopSteeringAvailable, playing, run.events.length, setStepAndTab]);

  function togglePlay() {
    if (playing) {
      setPlaying(false);
      return;
    }
    if (activeStep >= run.events.length) {
      setStepAndTab(1, { keepPlaying: true });
    }
    setPlaying(true);
  }

  function applySteering() {
    const steeringRun = resolvePolicyRun(DEFAULT_TASK_ID, 'baseline_with_steering');
    const steeringEvent = steeringRun.events.find((event) => event.action === 'ASK_USER') ?? steeringRun.events[0];
    setPolicyOptionId('baseline_with_steering');
    setSteeringDeclined(false);
    setActiveStep(steeringEvent.step);
    setTab(tabForEvent(steeringEvent));
    setPlaying(true);
  }

  function declineSteering() {
    const nextStep = Math.min(run.events.length, activeStep + 1);
    const nextEvent = findEvent(run.events, nextStep);
    setSteeringDeclined(true);
    setActiveStep(nextStep);
    setTab(tabForEvent(nextEvent));
    setPlaying(true);
  }

  function renderSteeringBranch(event: TraceEvent) {
    if (event.id !== activeEvent.id || !loopSteeringAvailable) return null;
    return (
      <div className="ml-7 mt-2 rounded-md border border-assist/40 bg-assist/10 p-3">
        <div className="flex items-center gap-2 text-xs font-medium text-assist">
          <GitBranch className="size-4" aria-hidden="true" />
          Human steering available
        </div>
        <p className="mt-1 text-xs leading-relaxed text-text-muted">
          The agent is stuck. Offer a hint, or let it continue and watch it fail.
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          <button
            type="button"
            className="focus-ring inline-flex min-h-8 items-center rounded-md bg-text px-3 text-xs font-medium text-page hover:bg-text/90"
            onClick={applySteering}
          >
            Apply steering
          </button>
          <button
            type="button"
            className="focus-ring inline-flex min-h-8 items-center rounded-md bg-surface-2 px-3 text-xs font-medium text-text hover:bg-surface-raised"
            onClick={declineSteering}
          >
            Let agent continue
          </button>
        </div>
      </div>
    );
  }

  return (
    <section id="cockpit" className="border-b border-border-subtle" aria-label="Interactive cockpit">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 md:py-20 lg:px-8">
        <div className="mb-6 flex flex-col justify-between gap-3 lg:flex-row lg:items-end">
          <div>
            <p className="section-chapter">
              <span className="text-text-muted">05</span>
              <span className="mx-2 text-text-muted">—</span>
              <span className="section-label">cockpit</span>
              <span className="sr-only">Interactive cockpit</span>
            </p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-text sm:text-3xl">
              Replay a real failure, then fix the harness
            </h2>
          </div>
          <p className="max-w-2xl text-xs leading-relaxed text-text-muted sm:text-sm">
            Press play to watch the baseline agent loop and get rejected. Toggle{' '}
            <span className="font-mono text-text-muted">Guarded Recovery</span> and watch the same task land green. At
            the loop moment in baseline, an option to apply human steering appears.
          </p>
        </div>

        <div className="rounded-2xl border border-border-subtle bg-surface/60 p-4 backdrop-blur md:p-5">
          <div className="grid min-w-0 grid-cols-1 gap-4 lg:grid-cols-[260px_minmax(0,1fr)_340px]">
            <aside className="space-y-4">
              <div className="rounded-lg border border-border-subtle bg-surface-2/40 p-3">
                <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Task</div>
                <div className="mt-2 font-mono text-[10px] uppercase tracking-wider text-text-faint">
                  {task.typeLabel}
                </div>
                <h3 className="mt-1 text-sm font-medium leading-snug text-text">{task.title}</h3>
                <p className="mt-2 text-xs leading-relaxed text-text-muted">{task.issue}</p>
                <div className="mt-3 space-y-1 text-xs">
                  <div className="flex items-baseline gap-2">
                    <span className="w-16 shrink-0 text-text-faint">success</span>
                    <span className="break-all font-mono text-text-muted">{task.successCommand}</span>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="w-16 shrink-0 text-text-faint">watched</span>
                    <span className="text-text-muted">{task.failureModes.join(', ')}</span>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border border-border-subtle bg-surface-2/40 p-3">
                <div id="cockpit-policy-label" className="font-mono text-[10px] uppercase tracking-wider text-text-faint">
                  Policy
                </div>
                <div className="mt-2 space-y-1.5" role="group" aria-labelledby="cockpit-policy-label">
                  {options.map((id, index) => {
                    const meta = policyOptionMeta(activeTaskId, id);
                    return (
                      <button
                        key={id}
                        type="button"
                        aria-pressed={id === policyOptionId}
                        aria-label={`${meta.name}. ${meta.description}`}
                        onClick={() => selectPolicy(id)}
                        className={clsx(
                          'focus-ring w-full rounded-md border px-2.5 py-2 text-left text-xs transition',
                          id === policyOptionId ? selectableActiveClass : selectableIdleClass
                        )}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-medium text-text">{meta.name}</span>
                          <span className="flex items-center gap-1">
                            {meta.badge ? (
                              <span className="rounded border border-border-subtle px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-wide text-text-faint">
                                {meta.badge}
                              </span>
                            ) : null}
                            <span className="font-mono text-[10px] text-text-faint">{index + 1}</span>
                          </span>
                        </div>
                        <p className="mt-0.5 leading-snug text-text-faint">{meta.description}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              <p id="cockpit-task-hint" className="text-[10px] leading-4 text-text-faint">
                Keyboard: <span className="font-mono">[ ]</span> tasks ·{' '}
                <span className="font-mono">1-{options.length}</span> policies ·{' '}
                <span className="font-mono">← →</span> steps · <span className="font-mono">f t d j r</span> evidence tabs
              </p>
            </aside>

            <main className="min-w-0">
              <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    className="focus-ring inline-flex size-8 items-center justify-center rounded-md bg-surface-2 text-text hover:bg-surface-raised"
                    onClick={() => setStepAndTab(activeStep - 1)}
                    aria-label="Previous trace step"
                  >
                    <SkipBack className="size-4" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    className="focus-ring inline-flex size-8 items-center justify-center rounded-md bg-text text-page hover:bg-text/90"
                    onClick={togglePlay}
                    aria-label={playing ? 'Pause trace replay' : 'Play trace replay'}
                  >
                    {playing ? <Pause className="size-4" aria-hidden="true" /> : <Play className="size-4" aria-hidden="true" />}
                  </button>
                  <button
                    type="button"
                    className="focus-ring inline-flex size-8 items-center justify-center rounded-md bg-surface-2 text-text hover:bg-surface-raised"
                    onClick={() => setStepAndTab(activeStep + 1)}
                    aria-label="Next trace step"
                  >
                    <SkipForward className="size-4" aria-hidden="true" />
                  </button>
                  <button
                    type="button"
                    className="focus-ring inline-flex min-h-8 items-center gap-2 rounded-md px-3 text-xs font-medium text-text hover:bg-surface-2"
                    onClick={resetReplay}
                  >
                    <RotateCcw className="size-3.5" aria-hidden="true" />
                    Reset
                  </button>
                </div>
                <div className="font-mono text-xs text-text-faint">
                  event {Math.min(activeStep, run.events.length)} / {run.events.length}
                </div>
              </div>

              <motion.div
                key={replayKey}
                initial={reduceMotion ? false : { opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: reduceMotion ? 0 : 0.25 }}
              >
                <div className="max-h-[min(70vh,720px)] overflow-y-auto overscroll-y-contain pr-0.5 lg:max-h-none lg:overflow-visible">
                  <TraceTimeline
                    events={run.events}
                    activeStep={activeStep}
                    onSelect={setStepAndTab}
                    policyName={run.name}
                    renderAfterEvent={renderSteeringBranch}
                  />
                </div>
              </motion.div>
            </main>

            <aside className="min-w-0 space-y-3">
              <VerdictStamp
                policyKey={`${activeTaskId}-${policyOptionId}-${replayPolicyId}`}
                verdict={run.verdict}
                label={verdictLabel(run.verdict)}
                reason={run.primaryReason}
              />
              <EvidencePanel
                run={run}
                activeEvent={activeEvent}
                tab={tab}
                onTabChange={setTab}
                knownFiles={task.knownFiles}
              />
              <ObservabilityLinks taskId={activeTaskId} policyId={replayPolicyId} />
            </aside>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-4" aria-live="polite" aria-label="Eval metrics">
            <MetricCard label="task success" value={`${Math.round(run.metrics.taskSuccess * 100)}%`} />
            <MetricCard label="recovery" value={`${Math.round(run.metrics.recoveryScore * 100)}%`} />
            <MetricCard label="loop rate" value={`${Math.round(run.metrics.loopScore * 100)}%`} />
            <MetricCard
              label={activeTaskId === 'adversarial_env_001' ? 'unsafe' : 'human'}
              value={formatMetric(
                activeTaskId === 'adversarial_env_001' ? run.metrics.unsafeAttempts : run.metrics.humanInterventions
              )}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
