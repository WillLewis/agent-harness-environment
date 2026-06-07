import linksData from '../../../data/evals/observability_links.json';

export type ObservabilityLink = {
  braintrustUrl: string | null;
  braintrustExperimentId: string | null;
  wandbUrl: string | null;
  wandbRunId: string | null;
  lastObservedAt: string | null;
  observabilityMode: string;
};

type RawLink = {
  braintrust_url?: string | null;
  braintrust_experiment_id?: string | null;
  wandb_url?: string | null;
  wandb_run_id?: string | null;
  last_observed_at?: string | null;
  observability_mode?: string | null;
};

type ObservabilityArtifact = {
  observability_version?: string;
  observability_mode?: string;
  generated_at?: string | null;
  runs?: Record<string, RawLink>;
};

const artifact = linksData as ObservabilityArtifact;

export const observabilityMode = artifact.observability_mode ?? 'off';

function runKey(taskId: string, policyId: string) {
  return `${taskId}::${policyId}`;
}

function hasVendorLink(raw: RawLink): boolean {
  return Boolean(raw.braintrust_url || raw.wandb_url);
}

/**
 * Returns exported observability links for a task/policy run, or null when no
 * vendor evidence was exported. The hosted app never fetches from vendors — it
 * only reads this static JSON, so an empty artifact renders nothing.
 */
export function getObservabilityLink(taskId: string, policyId: string): ObservabilityLink | null {
  const raw = artifact.runs?.[runKey(taskId, policyId)];
  if (!raw || !hasVendorLink(raw)) {
    return null;
  }
  return {
    braintrustUrl: raw.braintrust_url ?? null,
    braintrustExperimentId: raw.braintrust_experiment_id ?? null,
    wandbUrl: raw.wandb_url ?? null,
    wandbRunId: raw.wandb_run_id ?? null,
    lastObservedAt: raw.last_observed_at ?? null,
    observabilityMode: raw.observability_mode ?? observabilityMode
  };
}

export const hasAnyObservabilityLinks = Object.values(artifact.runs ?? {}).some(hasVendorLink);
