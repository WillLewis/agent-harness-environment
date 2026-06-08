'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import clsx from 'clsx';
import { motion, useReducedMotion } from 'framer-motion';
import { Pause, Play, RotateCcw, SkipBack, SkipForward } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { TraceTimeline } from './TraceTimeline';
import { EvidencePanel } from './EvidencePanel';
import { VerdictStamp } from './VerdictStamp';
import { ObservabilityLinks } from './ObservabilityLinks';
import { defaultTabForRun, findEvent, tabForEvent } from '../lib/cockpitEvidence';
import {
  cockpitTaskOrder,
  getCockpitTask,
  type EvidenceTab,
  type RunVariantId,
  type TaskId
} from '../lib/demoData';
import { selectableActiveClass, selectableIdleClass } from '../lib/statusStyles';

type CockpitProps = {
  activeTaskId: TaskId;
  onTaskChange: (taskId: TaskId) => void;
  autoplayToken: number;
};

function verdictLabel(verdict: string) {
  if (verdict === 'accepted') return 'ACCEPTED BY JUDGE';
  if (verdict === 'assisted') return 'ACCEPTED WITH STEERING';
  return 'REJECTED BY JUDGE';
}

function formatMetric(value: number) {
  return Number.isInteger(value) ? value : value.toFixed(2);
}

function variantDisplayName(variantId: string): string {
  if (variantId === 'claude-haiku-4-5') return 'Haiku 4.5';
  if (variantId === 'claude-sonnet-4-6') return 'Sonnet 4.6';
  if (variantId === 'claude-opus-4-8') return 'Opus 4.8';
  return variantId;
}

function resolveVariantRun(taskId: TaskId, variantId: RunVariantId) {
  const task = getCockpitTask(taskId);
  const run = task.variants[variantId];
  if (!run) {
    const fallback = task.variantOrder[0];
    return task.variants[fallback]!;
  }
  return run;
}

function resolveVariantId(taskId: TaskId, variantId: RunVariantId): RunVariantId {
  const task = getCockpitTask(taskId);
  return task.variants[variantId] ? variantId : task.variantOrder[0];
}

function variantOptionMeta(taskId: TaskId, variantId: RunVariantId) {
  const run = getCockpitTask(taskId).variants[variantId];
  return run
    ? { name: run.name, description: run.description, badge: null }
    : { name: variantDisplayName(variantId), description: '', badge: null };
}

function firstTabForRun(taskId: TaskId, variantId: RunVariantId) {
  const run = resolveVariantRun(taskId, variantId);
  const firstEvent = run.events[0];
  return firstEvent ? tabForEvent(firstEvent) : defaultTabForRun(variantId, taskId, run.events);
}

export function Cockpit({ activeTaskId, onTaskChange, autoplayToken }: CockpitProps) {
  const reduceMotion = useReducedMotion();
  const task = getCockpitTask(activeTaskId);
  const [variantId, setVariantId] = useState<RunVariantId>(task.defaultVariantId);
  const [activeStep, setActiveStep] = useState(1);
  const [tab, setTab] = useState<EvidenceTab>('terminal');
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<number | null>(null);

  const options = useMemo(() => task.variantOrder, [task.variantOrder]);
  const replayVariantId = resolveVariantId(activeTaskId, variantId);
  const run = resolveVariantRun(activeTaskId, replayVariantId);
  const activeEvent = useMemo(() => findEvent(run.events, activeStep), [run.events, activeStep]);
  const replayKey = `${activeTaskId}-${replayVariantId}`;

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

  const selectVariant = useCallback(
    (next: RunVariantId, nextOptions?: { autoplay?: boolean }) => {
      const nextReplayVariant = resolveVariantId(activeTaskId, next);
      const nextRun = resolveVariantRun(activeTaskId, nextReplayVariant);
      const firstEvent = nextRun.events[0];
      setVariantId(next);
      setActiveStep(1);
      setTab(
        firstEvent
          ? tabForEvent(firstEvent)
          : defaultTabForRun(nextReplayVariant, activeTaskId, nextRun.events)
      );
      setPlaying(Boolean(nextOptions?.autoplay));
    },
    [activeTaskId]
  );

  const resetReplay = useCallback(() => {
    setActiveStep(1);
    setPlaying(false);
    setTab(firstTabForRun(activeTaskId, replayVariantId));
  }, [activeTaskId, replayVariantId]);

  useEffect(() => {
    const defaultVariant = getCockpitTask(activeTaskId).defaultVariantId;
    setVariantId(defaultVariant);
    setActiveStep(1);
    setPlaying(false);
    setTab(firstTabForRun(activeTaskId, defaultVariant));
  }, [activeTaskId]);

  useEffect(() => {
    if (autoplayToken <= 0) return;
    const defaultVariant = getCockpitTask(activeTaskId).defaultVariantId;
    setVariantId(defaultVariant);
    setActiveStep(1);
    setTab(firstTabForRun(activeTaskId, defaultVariant));
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

      const variantIndex = Number(event.key) - 1;
      if (variantIndex >= 0 && variantIndex < options.length) {
        event.preventDefault();
        selectVariant(options[variantIndex]);
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
  }, [activeStep, activeTaskId, options, selectVariant, selectTask, setStepAndTab]);

  useEffect(() => {
    if (!playing) return;
    if (activeStep >= run.events.length) {
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
  }, [activeStep, playing, run.events.length, setStepAndTab]);

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
              Replay a real run, then watch the held-out battery decide
            </h2>
          </div>
          <p className="max-w-2xl text-xs leading-relaxed text-text-muted sm:text-sm">
            Press play to watch a model clear the visible suite and still get rejected. Toggle the{' '}
            <span className="font-mono text-text-muted">stronger model</span> and watch the same task pass the held-out
            battery. The visible suite agrees with both — only the held-out check separates them.
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
                <div id="cockpit-model-label" className="font-mono text-[10px] uppercase tracking-wider text-text-faint">
                  Model
                </div>
                <div className="mt-2 space-y-1.5" role="group" aria-labelledby="cockpit-model-label">
                  {options.map((id, index) => {
                    const meta = variantOptionMeta(activeTaskId, id);
                    return (
                      <button
                        key={id}
                        type="button"
                        aria-pressed={id === replayVariantId}
                        aria-label={`${meta.name}. ${meta.description}`}
                        onClick={() => selectVariant(id)}
                        className={clsx(
                          'focus-ring w-full rounded-md border px-2.5 py-2 text-left text-xs transition',
                          id === replayVariantId ? selectableActiveClass : selectableIdleClass
                        )}
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-medium text-text">{meta.name}</span>
                          <span className="flex items-center gap-1">
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
                <span className="font-mono">1-{options.length}</span> models ·{' '}
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
                  />
                </div>
              </motion.div>
            </main>

            <aside className="min-w-0 space-y-3">
              <VerdictStamp
                policyKey={replayKey}
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
              <ObservabilityLinks taskId={activeTaskId} policyId={replayVariantId} />
            </aside>
          </div>

          <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-4" aria-live="polite" aria-label="Eval metrics">
            <MetricCard label="task success" value={`${Math.round(run.metrics.taskSuccess * 100)}%`} />
            <MetricCard label="held-out" value={`${Math.round(run.metrics.recoveryScore * 100)}%`} />
            <MetricCard label="tool calls" value={formatMetric(run.metrics.toolCalls)} />
            <MetricCard label="verdict" value={run.verdict === 'accepted' ? 'pass' : 'fail'} />
          </div>
        </div>
      </div>
    </section>
  );
}
