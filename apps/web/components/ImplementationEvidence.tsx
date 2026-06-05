import {
  cursorArtifacts,
  implementationStats,
  keyCommands,
  statusLabels,
  systemCapabilities,
  type CapabilityStatus
} from '../lib/implementationEvidence';

const statusStyles: Record<
  CapabilityStatus,
  { badge: string; dot: string }
> = {
  implemented: {
    badge: 'border-emerald-400/30 bg-emerald-400/10 text-emerald-100',
    dot: 'bg-emerald-400'
  },
  local_dry_run: {
    badge: 'border-amber-400/30 bg-amber-400/10 text-amber-100',
    dot: 'bg-amber-400'
  },
  future: {
    badge: 'border-white/15 bg-white/[0.04] text-slate-400',
    dot: 'bg-slate-500'
  }
};

export function ImplementationEvidence() {
  return (
    <section
      id="architecture"
      aria-labelledby="architecture-heading"
      className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8"
    >
      <div className="max-w-3xl">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Implementation evidence</p>
        <h2 id="architecture-heading" className="mt-3 text-3xl font-semibold text-white">
          What this repo implements today
        </h2>
        <p className="mt-4 text-sm leading-7 text-slate-400">
          The hosted page is a static flight recorder. Local Python evals, the runner, MCP tools, and export adapters
          live in-repo; nothing here calls a live LLM or backend API at runtime.
        </p>
      </div>

      <dl className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <dt className="text-xs uppercase tracking-wider text-slate-500">Task fixtures</dt>
          <dd className="mt-2 font-mono text-2xl text-cyan-100">{implementationStats.taskCount}</dd>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <dt className="text-xs uppercase tracking-wider text-slate-500">Trace fixtures</dt>
          <dd className="mt-2 font-mono text-2xl text-cyan-100">{implementationStats.traceCount}</dd>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <dt className="text-xs uppercase tracking-wider text-slate-500">Deterministic scorers</dt>
          <dd className="mt-2 font-mono text-2xl text-cyan-100">{implementationStats.scorerCount}</dd>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
          <dt className="text-xs uppercase tracking-wider text-slate-500">Failure clusters</dt>
          <dd className="mt-2 font-mono text-2xl text-cyan-100">{implementationStats.failureClusterCount}</dd>
        </div>
      </dl>

      <div className="mt-10 overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03]">
        <div className="border-b border-white/10 p-5">
          <h3 className="text-lg font-semibold text-white">System map</h3>
          <p className="mt-2 text-sm text-slate-400">
            Status reflects the current repository — not a roadmap slide.
          </p>
          <ul className="mt-4 flex flex-wrap gap-3 text-xs" aria-label="Status legend">
            {(Object.keys(statusLabels) as CapabilityStatus[]).map((status) => (
              <li
                key={status}
                className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 ${statusStyles[status].badge}`}
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${statusStyles[status].dot}`}
                  aria-hidden="true"
                />
                {statusLabels[status]}
              </li>
            ))}
          </ul>
        </div>
        <ul className="divide-y divide-white/10">
          {systemCapabilities.map((capability) => {
            const styles = statusStyles[capability.status];
            return (
              <li key={capability.id} className="p-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <h4 className="text-base font-semibold text-white">{capability.title}</h4>
                  <span
                    className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs ${styles.badge}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} aria-hidden="true" />
                    {statusLabels[capability.status]}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{capability.description}</p>
                <p className="mt-3 font-mono text-xs text-slate-500">
                  {capability.repoPaths.join(' · ')}
                </p>
                {capability.commands?.length ? (
                  <p className="mt-2 font-mono text-xs text-cyan-100/90">
                    {capability.commands.join(' · ')}
                  </p>
                ) : null}
              </li>
            );
          })}
        </ul>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <h3 className="text-lg font-semibold text-white">Verification commands</h3>
          <p className="mt-2 text-sm text-slate-400">
            Same gates as CI (<code className="text-cyan-100">.github/workflows/ci.yml</code>) plus optional
            export previews.
          </p>
          <ul className="mt-4 space-y-3">
            {keyCommands.map(({ label, command }) => (
              <li key={command} className="rounded-2xl border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase tracking-wider text-slate-500">{label}</p>
                <p className="mt-1 font-mono text-sm text-slate-200">{command}</p>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <h3 className="text-lg font-semibold text-white">Hosted vs local</h3>
          <ul className="mt-4 space-y-4 text-sm leading-6 text-slate-400">
            <li>
              <strong className="font-medium text-slate-200">Hosted (this page):</strong> imports{' '}
              <span className="font-mono text-cyan-100/90">data/traces/*.json</span> and{' '}
              <span className="font-mono text-cyan-100/90">data/evals/</span> at build time. Cockpit replay only.
            </li>
            <li>
              <strong className="font-medium text-slate-200">Local eval:</strong>{' '}
              <span className="font-mono text-cyan-100/90">packages/evals/</span> scores fixtures;{' '}
              <span className="font-mono text-cyan-100/90">pnpm eval:ci</span> fails on regression.
            </li>
            <li>
              <strong className="font-medium text-slate-200">Adapters:</strong> Braintrust and Weave export shapes
              are previewed via dry-run — no API key required for development or CI.
            </li>
          </ul>
          <div className="mt-6">
            <p className="text-xs uppercase tracking-wider text-slate-500">Cursor workflow artifacts</p>
            <ul className="mt-3 grid gap-2 font-mono text-xs text-slate-300 sm:grid-cols-2">
              {cursorArtifacts.map((item) => (
                <li key={item} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2">
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
