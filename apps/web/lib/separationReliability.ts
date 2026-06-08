import completenessFixture from '../../../data/evals/reliability_completeness_comments_001.json';
import compatFixture from '../../../data/evals/reliability_compat_alias_migration_001.json';
import latentFixture from '../../../data/evals/reliability_latent_defects_001.json';

// The real model-tier held-out data behind the cockpit cards. Each fixture is a
// grid of {model × policy} cells generated offline by the eval runner. The visible
// suite passes for every model (visibleRate ≈ 1.0); the held-out mean-fraction is
// what actually separates the model tier — that's the whole point of these panels.

type FixtureCell = {
  model: string;
  policy: string;
  meanFraction: number;
  stdevFraction: number;
  visibleRate: number;
  completeRate: number;
  itemPassRates: Record<string, number>;
  patch_kinds: Record<string, number>;
  n_effective: number;
};

type Fixture = {
  task: string;
  n: number;
  models: string[];
  policies: string[];
  grading: string;
  cells: FixtureCell[];
};

/** One model's outcome on a card, baseline policy. Raw fractions — round at render. */
export type ModelTierPoint = {
  model: string;
  modelLabel: string;
  /** Visible-suite pass rate — flat ≈ 1.0 for every model. */
  visible: number;
  /** Held-out mean-fraction — the real capability gradient. */
  heldOut: number;
  /** Share of seeds that pass the held-out battery completely. */
  complete: number;
  /** Stdev of the held-out fraction across seeds. */
  stdev: number;
  /** Per-item held-out pass rates (name → rate), baseline policy. */
  itemPassRates: Record<string, number>;
};

export type CardReliability = {
  taskId: string;
  cardLabel: string;
  axis: string;
  /** Baseline-policy points, ordered nano → opus. */
  models: ModelTierPoint[];
};

/** Display labels per model id (nano → opus). */
const MODEL_LABELS: Record<string, string> = {
  'gpt-5.4-nano': 'GPT-5.4-nano',
  'gpt-5.4-mini': 'GPT-5.4-mini',
  'claude-haiku-4-5': 'Haiku 4.5',
  'claude-sonnet-4-6': 'Sonnet 4.6',
  'claude-opus-4-8': 'Opus 4.8'
};

/** Canonical left → right order for every panel. */
export const modelOrder: string[] = [
  'gpt-5.4-nano',
  'gpt-5.4-mini',
  'claude-haiku-4-5',
  'claude-sonnet-4-6',
  'claude-opus-4-8'
];

export function modelLabel(model: string): string {
  return MODEL_LABELS[model] ?? model;
}

const cardMeta: Record<string, { cardLabel: string; axis: string }> = {
  completeness_comments_001: {
    cardLabel: 'Strip both comment styles',
    axis: 'conjunctive completeness'
  },
  compat_alias_migration_001: {
    cardLabel: 'customer_id → account_id migration',
    axis: 'whole-repo back-compat'
  },
  latent_defects_001: {
    cardLabel: 'Fix split_bill + review the module',
    axis: 'latent-defect discovery'
  }
};

function buildCard(fixture: Fixture): CardReliability {
  const meta = cardMeta[fixture.task] ?? { cardLabel: fixture.task, axis: fixture.grading };
  const baselineCells = fixture.cells.filter((cell) => cell.policy === 'baseline');

  const models: ModelTierPoint[] = modelOrder
    .map((model) => baselineCells.find((cell) => cell.model === model))
    .filter((cell): cell is FixtureCell => Boolean(cell))
    .map((cell) => ({
      model: cell.model,
      modelLabel: modelLabel(cell.model),
      visible: cell.visibleRate,
      heldOut: cell.meanFraction,
      complete: cell.completeRate,
      stdev: cell.stdevFraction,
      itemPassRates: cell.itemPassRates
    }));

  return {
    taskId: fixture.task,
    cardLabel: meta.cardLabel,
    axis: meta.axis,
    models
  };
}

// Ordered [A completeness, B compat, C latent] to match the cockpit card order.
export const cardReliability: CardReliability[] = [
  buildCard(completenessFixture as Fixture),
  buildCard(compatFixture as Fixture),
  buildCard(latentFixture as Fixture)
];

/** How many real-model runs back each cell (shared n across fixtures). */
export const runsPerCell: number = (completenessFixture as Fixture).n;
