import { DemoFlow } from '../components/DemoFlow';
import { CapabilityValueChart } from '../components/CapabilityValueChart';
import { EvalTable } from '../components/EvalTable';
import { ReliabilityPanel } from '../components/ReliabilityPanel';
import { FailureTaxonomySection } from '../components/FailureTaxonomySection';
import { HarnessPrimitives } from '../components/HarnessPrimitives';
import { ImplementationEvidence } from '../components/ImplementationEvidence';
import { SectionHeader } from '../components/SectionHeader';
import { SurfaceCard } from '../components/ui/SurfaceCard';
import { TakeawaysSection } from '../components/TakeawaysSection';
import { getCockpitTask } from '../lib/demoData';

const premisePillars = [
  {
    title: 'Agents act invisibly',
    body: 'A coding agent emits plans, reads, edits, and shell calls. Without a trace, failure looks like a wall of text instead of a signal.'
  },
  {
    title: 'The visible suite lies',
    body: "An agent's own checks pass for every model — nano to frontier. They clear the happy path while missing malformed inputs, broken legacy callers, and unreviewed neighbouring defects."
  },
  {
    title: 'The held-out battery decides',
    body: 'Scoring each run against a held-out suite it never sees is what separates real model capability. Same repo, same task, same green visible suite — different model, different held-out outcome.'
  }
] as const;

const protocolEvents = [
  'PLAN',
  'READ_FILE',
  'SEARCH',
  'EDIT',
  'TERMINAL',
  'TEST',
  'RETRY',
  'BLOCKED_ACTION',
  'POLICY_DECISION',
  'FINAL'
] as const;

const protocolCards = [
  ['task_success', 'Whether the submitted patch passes target tests and expected behavior.'],
  ['recovery_rate', 'Whether the agent used new evidence after a failed command or test.'],
  ['hallucinated_file', 'A referenced file, symbol, script, or dependency that does not exist.'],
  ['loop_rate', 'Repeated tool calls or commands without new information.'],
  ['human_steering_burden', 'How many times the developer had to redirect the agent.'],
  ['unsafe_tool_attempt', 'A blocked shell, file, network, or secret-access action.']
] as const;

const headlineTask = getCockpitTask('compat_alias_migration_001');
const heroRejected = headlineTask.variants['claude-sonnet-4-6']!;
const heroAccepted = headlineTask.variants['claude-opus-4-8']!;

function formatPct(value: number) {
  return `${Math.round(value * 100)}%`;
}

const heroMetrics = [
  {
    label: 'task_success',
    baseline: formatPct(heroRejected.metrics.taskSuccess),
    guarded: formatPct(heroAccepted.metrics.taskSuccess)
  },
  {
    label: 'held_out',
    baseline: formatPct(heroRejected.metrics.recoveryScore),
    guarded: formatPct(heroAccepted.metrics.recoveryScore)
  },
  {
    label: 'verdict',
    baseline: heroRejected.verdict === 'accepted' ? 'pass' : 'fail',
    guarded: heroAccepted.verdict === 'accepted' ? 'pass' : 'fail'
  }
] as const;

export default function Home() {
  return (
    <main className="min-w-0">
      {/* Hero */}
      <section id="top" className="relative overflow-hidden border-b border-border-subtle">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 dot-bg opacity-70 [mask-image:radial-gradient(110%_85%_at_50%_0%,black,transparent)]"
        />
        <div className="relative mx-auto min-w-0 max-w-7xl px-4 py-16 sm:px-6 sm:py-20 lg:px-8 lg:py-24">
          <span className="inline-flex items-center rounded-full border border-border-subtle bg-surface px-3 py-1 font-mono text-[10px] uppercase tracking-widest text-text-faint">
            Hosted demo · precomputed traces
          </span>
          <h1 className="mt-5 max-w-4xl text-4xl font-bold tracking-tight text-text sm:text-5xl lg:text-6xl">
            Agent Harness Environment
          </h1>
          <p className="mt-4 max-w-3xl text-xl font-medium tracking-tight text-text-muted sm:text-2xl">
            A flight recorder for coding agents.
          </p>
          <p className="mt-5 max-w-2xl text-sm leading-relaxed text-text-muted sm:text-base">
            <span className="text-text">Static hosted demo</span>: replay precomputed real-model traces for
            completeness, back-compat migration, and latent-defect discovery tasks.{' '}
            <span className="text-text">No live LLM</span>, runner, or API calls in the browser.
          </p>
          <p className="mt-4 font-mono text-xs text-accent-muted sm:text-sm">
            Same repo. Same task. Different model. The visible suite passes — the held-out battery decides.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <a href="#cockpit" className="btn-primary">
              Replay the failure
            </a>
            <a href="#evals" className="btn-secondary">
              View eval report
            </a>
            <a href="#architecture" className="btn-secondary">
              Implementation map
            </a>
          </div>

          <div className="mt-12 max-w-3xl">
            <p className="font-mono text-[10px] uppercase tracking-widest text-text-faint">
              Real run · back-compat migration · Sonnet 4.6 → Opus 4.8
            </p>
            <div className="mt-3 grid gap-3 sm:grid-cols-3">
              {heroMetrics.map((metric) => (
                <div key={metric.label} className="rounded-lg border border-border-subtle bg-surface/60 px-3 py-2.5">
                  <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">{metric.label}</div>
                  <div className="mt-1.5 flex items-baseline gap-2 font-mono text-sm">
                    <span className="text-danger line-through decoration-danger/40">{metric.baseline}</span>
                    <span className="text-text-faint">→</span>
                    <span className="text-base text-success">{metric.guarded}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 01 — Premise */}
      <section id="premise" className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
        <SectionHeader
          chapter="01"
          label="premise"
          title="Why harnesses matter"
          description="When an agent fails, the product question is not only “was the model wrong?” The harness determines whether the agent plans, reads files, edits code, runs commands, recovers, asks for help, stops, or escalates."
        />
        <div className="mt-8 grid gap-3 md:grid-cols-3">
          {premisePillars.map((pillar) => (
            <SurfaceCard key={pillar.title}>
              <h3 className="text-sm font-semibold text-text">{pillar.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-text-muted">{pillar.body}</p>
            </SurfaceCard>
          ))}
        </div>
      </section>

      {/* 02 — Protocol / vocabulary */}
      <section id="protocol" className="mx-auto max-w-7xl px-4 pb-14 sm:px-6 sm:pb-16 lg:px-8">
        <SectionHeader
          chapter="02"
          label="vocabulary"
          title="The protocol we measure"
          description="Every run emits the same typed events and is scored against the same metrics. Both are deterministic — they ship in the repo as code, not vibes."
          className="mb-8"
        />
        <div className="space-y-8">
          <div>
            <h3 className="font-mono text-[11px] uppercase tracking-wider text-text-faint">events</h3>
            <div className="mt-3 flex flex-wrap gap-2">
              {protocolEvents.map((event) => (
                <code
                  key={event}
                  className="rounded-md border border-border-subtle bg-surface-2 px-2 py-1 font-mono text-[11px] text-text"
                >
                  {event}
                </code>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-mono text-[11px] uppercase tracking-wider text-text-faint">metrics</h3>
            <div className="mt-3 grid min-w-0 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {protocolCards.map(([title, body]) => (
                <div key={title} className="rounded-lg border border-border-subtle bg-surface-2/40 p-3.5">
                  <h4 className="font-mono text-sm text-text">{title}</h4>
                  <p className="mt-1.5 text-sm leading-relaxed text-text-muted">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 03 — Primitives */}
      <HarnessPrimitives />

      {/* 04 — Tasks + 05 — Cockpit */}
      <DemoFlow />

      {/* 06 — Failure taxonomy */}
      <FailureTaxonomySection />

      {/* 07 — Eval comparison */}
      <section id="evals" className="mx-auto min-w-0 max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
        <EvalTable />
        <ReliabilityPanel />
      </section>

      {/* 08 — Capability value */}
      <section id="capability-value" className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
        <SectionHeader
          chapter="08"
          label="capability value"
          title="The capability axis is real models now"
          description={
            <>
              The capability axis is no longer a synthetic knob — it&apos;s the real model tier (
              <span className="text-text">GPT-5.4-nano → Opus 4.8</span>). Each line is one task&apos;s held-out
              mean-fraction climbing across the tier, while the <span className="text-text">visible suite stays pinned
              at 1.0</span> for every model. The gap between the flat visible reference and each climbing line is exactly
              what the held-out battery buys you.
            </>
          }
          className="mb-8"
        />
        <CapabilityValueChart />
        <p className="mt-4 max-w-3xl text-[11px] leading-relaxed text-text-faint">
          Measured, not drawn: held-out mean-fraction per model from the real run fixtures (
          <code className="text-text-muted">data/evals/reliability_*.json</code>, baseline policy). Visible is 1.0 by
          construction; the separation is the held-out gradient.
        </p>
      </section>

      {/* 09 — Implementation evidence */}
      <ImplementationEvidence />

      {/* 10 — Takeaways */}
      <TakeawaysSection />
    </main>
  );
}
