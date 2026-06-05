import policyComparisonData from '../../../data/evals/policy_comparison.json';
import failureClustersData from '../../../data/failure_clusters.json';
import policies from '../../../data/policies.json';

export type PolicyComparisonRow = (typeof policyComparisonData)[number];

export type FailureCluster = (typeof failureClustersData)[number];

export type FailureClusterId = FailureCluster['id'];

const policyNameById = Object.fromEntries(
  (policies as Array<{ id: string; name: string }>).map((policy) => [policy.id, policy.name])
) as Record<string, string>;

export const policyComparison: PolicyComparisonRow[] = policyComparisonData;

export const failureClusters: FailureCluster[] = failureClustersData;

export function policyDisplayName(policyId: string): string {
  return policyNameById[policyId] ?? policyId.replace(/_/g, ' ');
}

export function getFailureCluster(clusterId: FailureClusterId): FailureCluster | undefined {
  return failureClusters.find((cluster) => cluster.id === clusterId);
}

export const BASELINE_LOOP_CLUSTER_ID = 'repeated_terminal_command' as const;
