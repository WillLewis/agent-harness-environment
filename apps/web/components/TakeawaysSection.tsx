import { SectionHeader } from './SectionHeader';
import { SurfaceCard } from './ui/SurfaceCard';

const takeaways = [
  {
    chapter: '01',
    text: 'The visible suite passes from the smallest model to the frontier — the held-out battery it never sees is what separates real capability on the same task and repo.'
  },
  {
    chapter: '02',
    text: 'Recovery behavior is traceable — every plan, read, edit, test, and block is a typed event you can replay.'
  },
  {
    chapter: '03',
    text: 'Scoring is deterministic and local. packages/evals and pnpm eval:ci gate regressions without a live LLM.'
  },
  {
    chapter: '04',
    text: 'Braintrust and W&B Weave export is wired and live — but optional and offline. The core harness stays fixture-driven; nothing calls a vendor at runtime.'
  }
] as const;

export function TakeawaysSection() {
  return (
    <section id="takeaways" className="mx-auto max-w-7xl px-4 py-14 pb-20 sm:px-6 sm:py-16 lg:px-8">
      <SectionHeader
        chapter="09"
        label="takeaways"
        title="What this demo proves."
        description="The visible suite passes from the smallest model to the frontier; the held-out battery it never sees is what separates real capability — traceable, deterministic, and reproducible locally."
        className="mb-8"
      />
      <ol className="grid gap-3 sm:grid-cols-2">
        {takeaways.map((item) => (
          <li key={item.chapter}>
            <SurfaceCard className="h-full">
              <p className="section-chapter">
                <span className="text-text-muted">{item.chapter}</span>
              </p>
              <p className="mt-2 text-sm leading-relaxed text-text-muted">{item.text}</p>
            </SurfaceCard>
          </li>
        ))}
      </ol>
    </section>
  );
}
