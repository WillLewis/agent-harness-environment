import policyComparisonData from '../../../data/evals/policy_comparison.json';
import failureClustersData from '../../../data/failure_clusters.json';
import reliabilityData from '../../../data/evals/reliability.json';
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
export const BASELINE_UNSAFE_CLUSTER_ID = 'unsafe_tool_attempt' as const;

// Real measured reliability — pass^k on the visible (naive) vs held-out (true)
// metric for all three toy tasks, generated offline by `python packages/evals/pass_k.py`.
export type ReliabilityReport = typeof reliabilityData;
export type ReliabilityTask = ReliabilityReport['tasks'][number];
export type ReliabilityPolicyRow = ReliabilityTask['policies'][number];

export const reliability: ReliabilityReport = reliabilityData;
export const reliabilityTasks: ReliabilityTask[] = reliability.tasks;

export function reliabilityTask(taskId: string): ReliabilityTask | undefined {
  return reliability.tasks.find((task) => task.task_id === taskId);
}

export function reliabilityPolicy(task: ReliabilityTask, policyId: string): ReliabilityPolicyRow | undefined {
  return task.policies.find((row) => row.policy === policyId);
}
