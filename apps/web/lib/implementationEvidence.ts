import tasks from '../../../data/tasks.json';
import failureClusters from '../../../data/failure_clusters.json';
import completenessHaikuRejected from '../../../data/cockpit_traces/completeness_haiku_rejected.json';
import completenessSonnetAccepted from '../../../data/cockpit_traces/completeness_sonnet_accepted.json';
import compatSonnetRejected from '../../../data/cockpit_traces/compat_sonnet_rejected.json';
import compatOpusAccepted from '../../../data/cockpit_traces/compat_opus_accepted.json';
import latentSonnetRejected from '../../../data/cockpit_traces/latent_sonnet_rejected.json';
import latentOpusPartial from '../../../data/cockpit_traces/latent_opus_partial.json';

export type CapabilityStatus = 'implemented' | 'local_dry_run' | 'future';

export type SystemCapability = {
  id: string;
  title: string;
  description: string;
  status: CapabilityStatus;
  repoPaths: string[];
  commands?: string[];
};

/** Ensures every trace import stays wired; count is derived from the manifest. */
export const traceFixtures = [
  completenessHaikuRejected,
  completenessSonnetAccepted,
  compatSonnetRejected,
  compatOpusAccepted,
  latentSonnetRejected,
  latentOpusPartial
] as const;

export const implementationStats = {
  taskCount: tasks.length,
  traceCount: traceFixtures.length,
  scorerCount: 10,
  failureClusterCount: failureClusters.length,
  policyComparisonPolicies: 5
};

export const keyCommands = [
  { label: 'CI smoke gate', command: 'pnpm eval:ci' },
  { label: 'Static eval suite', command: 'pnpm eval:suite' },
  { label: 'Fixture validation', command: 'pnpm validate:fixtures' },
  { label: 'Local runner (MVP)', command: 'python services/runner/run_task.py guarded_recovery' },
  { label: 'Braintrust export preview', command: 'pnpm export:braintrust:dry-run' },
  { label: 'Weave export preview', command: 'pnpm export:weave:dry-run' }
] as const;

export const statusLabels: Record<CapabilityStatus, string> = {
  implemented: 'Implemented now',
  local_dry_run: 'Local / dry-run',
  future: 'Future integration'
};

export const systemCapabilities: SystemCapability[] = [
  {
    id: 'hosted_cockpit',
    title: 'Static hosted cockpit',
    description:
      'Next.js demo replays precomputed traces. Model toggle updates timeline, metrics, terminal, diff, and verdict together — no live agent or API.',
    status: 'implemented',
    repoPaths: ['apps/web/components/Cockpit.tsx', 'apps/web/lib/cockpitFixtures.ts', 'data/cockpit_traces/']
  },
  {
    id: 'trace_fixtures',
    title: 'Trace fixtures',
    description:
      'Versioned AgentTraceEvent JSON drives the work: data/cockpit_traces/ feeds the hosted replay, data/traces/ feeds eval scoring and adapter export previews.',
    status: 'implemented',
    repoPaths: ['data/cockpit_traces/', 'data/traces/', 'packages/harness/', 'packages/evals/fixture_validation.py']
  },
  {
    id: 'deterministic_scorers',
    title: 'Deterministic scorers',
    description:
      'Python scorers (tests, regression, loop, safety, recovery, allowlist, contract consistency, etc.) produce inspectable pass/fail signals — not LLM-only judges.',
    status: 'implemented',
    repoPaths: ['packages/evals/scorers/', 'packages/evals/run_eval.py'],
    commands: ['pnpm eval', 'pnpm eval:baseline']
  },
  {
    id: 'eval_suite_ci',
    title: 'Eval suite + CI smoke gate',
    description:
      'run_suite scores every static trace and enforces gate expectations. GitHub Actions runs the same deterministic contract on push/PR.',
    status: 'implemented',
    repoPaths: ['packages/evals/run_suite.py', 'packages/evals/suite_gates.py', '.github/workflows/ci.yml'],
    commands: ['pnpm eval:ci', 'pnpm eval:suite']
  },
  {
    id: 'local_runner',
    title: 'Local runner MVP',
    description:
      'Copies toy repos into a sandbox, runs allow-listed commands, and emits traces under runs/ — separate from the hosted static demo.',
    status: 'implemented',
    repoPaths: ['services/runner/', 'toy_repos/'],
    commands: ['python services/runner/run_task.py guarded_recovery']
  },
  {
    id: 'mcp_tools',
    title: 'MCP tools',
    description:
      'Cursor MCP server exposes trace fetch, policy compare, failure-cluster lookup, and dataset promotion helpers for local workflow.',
    status: 'implemented',
    repoPaths: ['tools/mcp_server.py', 'tools/mcp_helpers.py', '.cursor/mcp.json']
  },
  {
    id: 'braintrust_adapter',
    title: 'Braintrust dry-run adapter',
    description:
      'Maps tasks, traces, and scores to Braintrust-shaped dataset/example rows. Dry-run prints JSON; live upload is not wired yet.',
    status: 'local_dry_run',
    repoPaths: ['packages/evals/adapters/braintrust_adapter.py'],
    commands: ['pnpm export:braintrust:dry-run']
  },
  {
    id: 'weave_adapter',
    title: 'W&B Weave dry-run adapter',
    description:
      'Maps traces to span trees and scorer output to Weave feedback records. Requires weave/wandb + WANDB_API_KEY only for future live export.',
    status: 'local_dry_run',
    repoPaths: ['packages/evals/adapters/weave_adapter.py'],
    commands: ['pnpm export:weave:dry-run']
  },
  {
    id: 'external_live_export',
    title: 'Live Braintrust / Weave upload',
    description:
      'Optional experiment tracking and production trace ingestion when SDK credentials are configured.',
    status: 'future',
    repoPaths: ['packages/evals/adapters/']
  }
];

export const cursorArtifacts = [
  '.cursor/rules',
  '.cursor/skills',
  '.cursor/mcp.json',
  '.cursor/BUGBOT.md'
] as const;
