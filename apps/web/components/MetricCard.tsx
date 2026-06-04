type MetricCardProps = {
  label: string;
  value: string | number;
  help?: string;
};

export function MetricCard({ label, value, help }: MetricCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="text-xs uppercase tracking-[0.24em] text-slate-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
      {help ? <p className="mt-2 text-xs leading-5 text-slate-400">{help}</p> : null}
    </div>
  );
}
