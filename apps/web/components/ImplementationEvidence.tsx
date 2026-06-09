import { ExternalLink } from 'lucide-react';
import {
  implementationStats,
  statusLabels,
  systemCapabilities,
  type CapabilityStatus
} from '../lib/implementationEvidence';
import { SectionHeader } from './SectionHeader';
import { SurfaceCard } from './ui/SurfaceCard';

const statusStyles: Record<CapabilityStatus, { badge: string; dot: string }> = {
  implemented: {
    badge: 'border-success/30 bg-success/10 text-success',
    dot: 'bg-success'
  },
  local_dry_run: {
    badge: 'border-warning/30 bg-warning/10 text-warning',
    dot: 'bg-warning'
  },
  future: {
    badge: 'border-border-subtle bg-surface text-text-faint',
    dot: 'bg-text-faint'
  }
};

export function ImplementationEvidence() {
  return (
    <section
      id="architecture"
      aria-labelledby="architecture-heading"
      className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8"
    >
      <SectionHeader
        chapter="08"
        label="Architecture"
        title="What the repo actually implements today."
        titleId="architecture-heading"
        description="The building blocks behind the demo — trace fixtures, deterministic scorers, the eval suite + CI gate, the local runner, MCP tools, and live Braintrust / W&B export. Status reflects the current repository, not a roadmap; nothing here calls a live LLM at runtime."
      />

      <dl className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <SurfaceCard className="p-3 sm:p-4">
          <dt className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Task fixtures</dt>
          <dd className="mt-1.5 font-mono text-2xl tabular-nums text-accent-muted">{implementationStats.taskCount}</dd>
        </SurfaceCard>
        <SurfaceCard className="p-3 sm:p-4">
          <dt className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Real traces</dt>
          <dd className="mt-1.5 font-mono text-2xl tabular-nums text-accent-muted">{implementationStats.traceCount}</dd>
        </SurfaceCard>
        <SurfaceCard className="p-3 sm:p-4">
          <dt className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Deterministic scorers</dt>
          <dd className="mt-1.5 font-mono text-2xl tabular-nums text-accent-muted">{implementationStats.scorerCount}</dd>
        </SurfaceCard>
        <SurfaceCard className="p-3 sm:p-4">
          <dt className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Failure clusters</dt>
          <dd className="mt-1.5 font-mono text-2xl tabular-nums text-accent-muted">
            {implementationStats.failureClusterCount}
          </dd>
        </SurfaceCard>
      </dl>

      <div className="surface-card mt-6 overflow-hidden">
        <div className="border-b border-border-subtle p-4 sm:p-5">
          <h3 className="text-base font-semibold text-text">System map</h3>
          <p className="mt-1.5 text-xs leading-relaxed text-text-muted sm:text-sm">
            Status reflects the current repository — not a roadmap slide.
          </p>
          <ul className="mt-3 flex flex-wrap gap-2 text-xs" aria-label="Status legend">
            {(Object.keys(statusLabels) as CapabilityStatus[])
              .filter((status) => systemCapabilities.some((capability) => capability.status === status))
              .map((status) => (
                <li
                  key={status}
                  className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 font-mono text-[10px] ${statusStyles[status].badge}`}
                >
                  <span className={`h-1.5 w-1.5 rounded-full ${statusStyles[status].dot}`} aria-hidden="true" />
                  {statusLabels[status]}
                </li>
              ))}
          </ul>
        </div>
        <ul className="divide-y divide-border-subtle">
          {systemCapabilities.map((capability) => {
            const styles = statusStyles[capability.status];
            return (
              <li key={capability.id} className="min-w-0 p-4 sm:p-5">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h4 className="min-w-0 flex-1 text-sm font-semibold text-text sm:text-base">{capability.title}</h4>
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 font-mono text-[10px] ${styles.badge}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} aria-hidden="true" />
                    {statusLabels[capability.status]}
                  </span>
                </div>
                <p className="mt-1.5 text-xs leading-relaxed text-text-muted sm:text-sm">{capability.description}</p>
                <p className="mt-2 break-all font-mono text-[10px] leading-5 text-text-faint">
                  {capability.repoPaths.join(' · ')}
                </p>
                {capability.commands?.length ? (
                  <p className="mt-1.5 break-all font-mono text-[10px] leading-5 text-accent-muted">
                    {capability.commands.join(' · ')}
                  </p>
                ) : null}
                {capability.links?.length ? (
                  <p className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[10px] leading-5">
                    {capability.links.map((link) => (
                      <a
                        key={link.href}
                        href={link.href}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="focus-ring inline-flex items-center gap-1 text-accent-muted underline-offset-2 transition hover:underline"
                      >
                        {link.label}
                        <ExternalLink className="size-3" aria-hidden="true" />
                      </a>
                    ))}
                  </p>
                ) : null}
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
