type MetricCardProps = {
  label: string;
  value: string | number;
  help?: string;
};

export function MetricCard({ label, value, help }: MetricCardProps) {
  return (
    <div className="surface-card p-3">
      <div className="font-mono text-[10px] uppercase tracking-wider text-text-faint">{label}</div>
      <div className="mt-1 font-mono text-xl font-semibold tabular-nums text-text">{value}</div>
      {help ? <p className="mt-1.5 text-[11px] leading-5 text-text-faint">{help}</p> : null}
    </div>
  );
}
