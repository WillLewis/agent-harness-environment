import { SectionHeader } from './SectionHeader';
import { SurfaceCard } from './ui/SurfaceCard';

const primitives = [
  {
    title: 'Task fixtures',
    body: 'Curated coding tasks with known files, success commands, and failure modes — shipped as JSON under data/tasks/ and replayed in the cockpit.'
  },
  {
    title: 'Trace replay',
    body: 'Every run emits typed AgentTraceEvent steps. The hosted demo replays precomputed traces — no live agent in the browser.'
  },
  {
    title: 'Visible vs held-out suite',
    body: "The agent's own visible suite passes for every model; a held-out battery it never sees is scored alongside it. Same model and repo — the held-out fraction is what separates real capability."
  },
  {
    title: 'Deterministic scoring',
    body: 'packages/evals scores traces with explicit thresholds. Results are reproducible locally and in CI — not LLM vibes.'
  },
  {
    title: 'Failure clusters',
    body: 'The real held-out shapes (missed malformed delimiters, broken legacy callers, narrowed parsers, unreviewed neighbouring defects) are grouped with detection rules and recommended harness changes.'
  },
  {
    title: 'Local runner & CI gate',
    body: 'services/runner executes tasks in a sandbox; pnpm eval:ci enforces suite gates on fixture traces before merge.'
  }
] as const;

export function HarnessPrimitives() {
  return (
    <section id="primitives" className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8">
      <SectionHeader
        chapter="03"
        label="primitives"
        title="What the harness provides"
        description="Conceptual building blocks demonstrated by fixture traces — not a live runner on this page."
        className="mb-8"
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {primitives.map((item) => (
          <SurfaceCard key={item.title}>
            <h3 className="text-sm font-semibold text-text">{item.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-text-muted">{item.body}</p>
          </SurfaceCard>
        ))}
      </div>
    </section>
  );
}
