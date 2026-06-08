'use client';

import { useMemo, useState } from 'react';
import clsx from 'clsx';
import {
  AlertTriangle,
  BookOpen,
  Bug,
  ChevronDown,
  FileCode2,
  FileSearch,
  Network,
  Tag,
  Zap
} from 'lucide-react';
import { cockpitTaskOrder, getCockpitTask, type TaskId } from '../lib/demoData';
import { taskStories, type TaskStory } from '../lib/taskStories';

const typeIcons = {
  completeness: Bug,
  compat: Network,
  discovery: FileSearch
} as const;

type TasksSectionProps = {
  activeTaskId: TaskId;
  onTrigger: (taskId: TaskId) => void;
};

type TaskCardModel = ReturnType<typeof getCockpitTask> & {
  story: TaskStory;
};

export function TasksSection({ activeTaskId, onTrigger }: TasksSectionProps) {
  const [openTaskIds, setOpenTaskIds] = useState<TaskId[]>([]);
  const taskCards = useMemo<TaskCardModel[]>(
    () =>
      cockpitTaskOrder.map((taskId) => ({
        ...getCockpitTask(taskId),
        story: taskStories[taskId]
      })),
    []
  );

  function toggleStory(taskId: TaskId) {
    setOpenTaskIds((current) =>
      current.includes(taskId) ? current.filter((id) => id !== taskId) : [...current, taskId]
    );
  }

  return (
    <section id="tasks" className="border-b border-border-subtle" aria-label="Task stories">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 md:py-20 lg:px-8">
        <p className="section-chapter">
          <span className="text-text-muted">04</span>
          <span className="mx-2 text-text-muted">—</span>
          <span className="section-label">tasks</span>
        </p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-text sm:text-3xl">
          Three tasks. Three failure shapes.
        </h2>
        <p className="sr-only">COMPLETENESS COMPAT-MIGRATION LATENT-DEFECTS</p>
        <p className="mt-6 max-w-3xl text-sm leading-relaxed text-text-muted sm:text-base">
          Before you watch the cockpit replay, meet the work. Each task below is a real shape we see in production
          agent traces — a two-part completeness fix, a back-compat API migration, a latent-defect review. The visible
          suite passes for every model; the held-out battery is what separates them. Open{' '}
          <span className="font-mono text-text-muted">The Backstory</span> for the situation a PM would recognize, or
          hit <span className="font-mono text-text-muted">Trigger It</span> to load the task into the cockpit.
        </p>

        <div className="mt-6 grid items-start gap-4 md:grid-cols-3">
          {taskCards.map((task) => {
            const Icon = typeIcons[task.type];
            const isActive = task.id === activeTaskId;
            const isOpen = openTaskIds.includes(task.id);

            return (
              <article
                key={task.id}
                className={clsx(
                  'group relative overflow-hidden rounded-xl border bg-surface/50 transition-all hover:bg-surface-2/50',
                  isActive ? 'border-success/40 ring-1 ring-success/50' : 'border-border-subtle'
                )}
              >
                <div
                  aria-hidden="true"
                  className={clsx(
                    'absolute inset-y-0 left-0 w-px transition-colors',
                    isActive ? 'bg-success' : 'bg-info/0 group-hover:bg-info/60'
                  )}
                />

                <div className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex min-w-0 items-center gap-2">
                      <Icon className="size-4 shrink-0 text-info" aria-hidden="true" />
                      <span className="font-mono text-[10px] uppercase tracking-widest text-text-faint">
                        {task.typeLabel}
                      </span>
                    </div>
                    {isActive ? (
                      <span className="rounded-md border border-success/30 bg-success/15 px-2.5 py-0.5 font-mono text-[10px] font-semibold text-success">
                        in cockpit
                      </span>
                    ) : null}
                  </div>

                  <h3 className="mt-3 text-[15px] font-medium leading-snug tracking-tight text-text">{task.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-text-muted">{task.issue}</p>

                  <div className="mt-4 space-y-3">
                    <div className="flex flex-wrap gap-1">
                      {task.tags.map((tag) => (
                        <code
                          key={tag}
                          className="rounded border border-border-subtle bg-surface-2 px-1.5 py-0.5 font-mono text-[10px] text-text-muted"
                        >
                          {tag}
                        </code>
                      ))}
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        aria-expanded={isOpen}
                        onClick={() => toggleStory(task.id)}
                        className={clsx(
                          'focus-ring inline-flex min-h-8 items-center justify-center gap-2 rounded-md px-3 text-xs font-medium transition',
                          isOpen ? 'bg-text text-page' : 'bg-surface-2 text-text hover:bg-surface-raised'
                        )}
                      >
                        <BookOpen className="size-3.5" aria-hidden="true" />
                        The Backstory
                        <ChevronDown
                          className={clsx('size-3.5 transition-transform', isOpen ? 'rotate-180' : '')}
                          aria-hidden="true"
                        />
                      </button>
                      <button
                        type="button"
                        onClick={() => onTrigger(task.id)}
                        className="focus-ring group/btn inline-flex min-h-8 items-center justify-center gap-2 rounded-md bg-text px-3 text-xs font-medium text-page transition hover:bg-text/90"
                      >
                        <Zap className="size-3.5 transition-transform group-hover/btn:scale-110" aria-hidden="true" />
                        Trigger It
                      </button>
                    </div>
                  </div>
                </div>

                <div
                  className={clsx(
                    'grid transition-all duration-300 ease-out',
                    isOpen ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                  )}
                >
                  <div className="overflow-hidden">
                    <div className="space-y-4 border-t border-border-subtle bg-surface-2/30 px-5 pb-5 pt-1 text-sm">
                      <BackstoryBlock label="The setup" body={task.story.setting} />
                      <BackstoryBlock label="What's on the line" body={task.story.stakes} />

                      <div>
                        <div className="mb-1.5 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-warning">
                          <AlertTriangle className="size-3" aria-hidden="true" />
                          failure modes triggered
                        </div>
                        <div className="mb-2 flex flex-wrap gap-1">
                          {task.failureModes.map((mode) => (
                            <code
                              key={mode}
                              className="rounded border border-warning/30 bg-warning/10 px-1.5 py-0.5 text-[10px] text-warning"
                            >
                              {mode}
                            </code>
                          ))}
                        </div>
                        <p className="text-sm leading-relaxed text-text-muted">{task.story.failurePlay}</p>
                      </div>

                      <div>
                        <div className="mb-1.5 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-info">
                          <FileCode2 className="size-3" aria-hidden="true" />
                          why these files matter
                        </div>
                        <div className="mb-2 flex flex-wrap gap-1">
                          {task.expectedFiles.map((file) => (
                            <code
                              key={file}
                              className="rounded border border-border-subtle bg-surface-2 px-1.5 py-0.5 font-mono text-[10px] text-text/80"
                            >
                              {file}
                            </code>
                          ))}
                        </div>
                        <p className="text-sm leading-relaxed text-text-muted">{task.story.filesPlay}</p>
                      </div>

                      <div>
                        <div className="mb-1.5 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-widest text-text-faint">
                          <Tag className="size-3" aria-hidden="true" />
                          why these tags
                        </div>
                        <p className="text-sm leading-relaxed text-text-muted">{task.story.tagsPlay}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function BackstoryBlock({ label, body }: { label: string; body: string }) {
  return (
    <div>
      <div className="mb-1 font-mono text-[10px] uppercase tracking-widest text-text-faint">{label}</div>
      <p className="text-sm leading-relaxed text-text/85">{body}</p>
    </div>
  );
}
