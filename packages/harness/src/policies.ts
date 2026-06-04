export type HarnessPolicyId =
  | 'baseline'
  | 'test_first'
  | 'context_first'
  | 'guarded_recovery'
  | 'high_reasoning_on_failure'
  | 'rl_lite_router';

export type HarnessPolicy = {
  id: HarnessPolicyId;
  description: string;
  constraints: string[];
  maxRetries: number;
  requiresEvidenceAfterFailure: boolean;
};

export const harnessPolicies: Record<HarnessPolicyId, HarnessPolicy> = {
  baseline: {
    id: 'baseline',
    description: 'Broad freedom with minimal harness structure.',
    constraints: ['global safety layer'],
    maxRetries: 3,
    requiresEvidenceAfterFailure: false
  },
  test_first: {
    id: 'test_first',
    description: 'Requires test discovery or inspection before code edits.',
    constraints: ['identify target test', 'read or run test before edit'],
    maxRetries: 3,
    requiresEvidenceAfterFailure: true
  },
  context_first: {
    id: 'context_first',
    description: 'Requires relevant source context before patching.',
    constraints: ['read likely source files', 'search referenced symbols'],
    maxRetries: 3,
    requiresEvidenceAfterFailure: true
  },
  guarded_recovery: {
    id: 'guarded_recovery',
    description: 'Adds loop breakers, retry limits, blocked unsafe commands, and failure-output inspection.',
    constraints: ['max retry count', 'no repeated command without evidence', 'blocked unsafe commands'],
    maxRetries: 2,
    requiresEvidenceAfterFailure: true
  },
  high_reasoning_on_failure: {
    id: 'high_reasoning_on_failure',
    description: 'Escalates to stronger/slower reasoning only after evidence of failure.',
    constraints: ['failure threshold', 'explicit escalation reason'],
    maxRetries: 2,
    requiresEvidenceAfterFailure: true
  },
  rl_lite_router: {
    id: 'rl_lite_router',
    description: 'Selects among harness policies using contextual reward history.',
    constraints: ['logs policy decision', 'updates reward table after run'],
    maxRetries: 2,
    requiresEvidenceAfterFailure: true
  }
};
