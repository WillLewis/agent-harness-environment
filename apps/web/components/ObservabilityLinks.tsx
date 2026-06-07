import { ExternalLink } from 'lucide-react';
import { getObservabilityLink } from '../lib/observabilityLinks';

type ObservabilityLinksProps = {
  taskId: string;
  policyId: string;
};

/**
 * Restrained evidence affordance: renders external links to exported Braintrust
 * / W&B runs only when the static observability artifact has them. With
 * observability off (the default), this renders nothing.
 */
export function ObservabilityLinks({ taskId, policyId }: ObservabilityLinksProps) {
  const link = getObservabilityLink(taskId, policyId);
  if (!link) {
    return null;
  }

  const items = [
    link.braintrustUrl ? { label: 'Braintrust', href: link.braintrustUrl } : null,
    link.wandbUrl ? { label: 'W&B', href: link.wandbUrl } : null
  ].filter((item): item is { label: string; href: string } => item !== null);

  if (items.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-border-subtle bg-surface-2/40 p-3">
      <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">Observability</div>
      <div className="mt-2 space-y-1.5">
        {items.map((item) => (
          <a
            key={item.label}
            href={item.href}
            target="_blank"
            rel="noreferrer noopener"
            className="focus-ring flex items-center justify-between gap-2 rounded-md border border-border-subtle bg-surface px-2.5 py-1.5 text-xs text-text-muted transition hover:text-text"
          >
            <span className="font-mono text-[11px]">{item.label}</span>
            <ExternalLink className="size-3.5" aria-hidden="true" />
          </a>
        ))}
      </div>
    </div>
  );
}
