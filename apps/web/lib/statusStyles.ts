export function severityBadgeClass(severity: string) {
  if (severity === 'high') return 'border-danger/30 bg-danger/10 text-danger';
  if (severity === 'medium') return 'border-warning/30 bg-warning/10 text-warning';
  return 'border-border-subtle bg-surface text-text-muted';
}

export function verdictPanelClass(verdict: 'accepted' | 'rejected' | 'assisted') {
  if (verdict === 'rejected') return 'border-danger/30 bg-danger/10';
  if (verdict === 'assisted') return 'border-warning/30 bg-warning/10';
  return 'border-success/30 bg-success/10';
}

export function verdictTextClass(verdict: 'accepted' | 'rejected' | 'assisted') {
  if (verdict === 'rejected') return 'text-danger';
  if (verdict === 'assisted') return 'text-warning';
  return 'text-success';
}

export const selectableIdleClass =
  'border-border-subtle bg-surface hover:bg-surface-2';

export const selectableActiveClass = 'border-accent/45 bg-accent-subtle';
