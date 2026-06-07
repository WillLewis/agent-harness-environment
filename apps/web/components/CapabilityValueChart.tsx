'use client';

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import capabilityCurves from '../../../data/evals/capability_curves.json';

const SERIES = [
  { key: 'testFirstLift', name: 'test-first lift', color: '#5bb0d7', kind: 'productivity' },
  { key: 'contextFirstLift', name: 'context-first lift', color: '#9aa7c2', kind: 'productivity' },
  { key: 'baselineGamingRate', name: 'baseline spec-gaming rate', color: '#ea9344', kind: 'integrity' }
] as const;

type TooltipPayload = { dataKey: string; name: string; value: number; color: string };

function CapabilityTooltip({
  active,
  payload,
  label
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: number;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-border bg-elevated px-3 py-2 text-xs shadow-lg">
      <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-text-faint">capability {label}</div>
      {payload.map((entry) => (
        <div key={entry.dataKey} className="flex items-center justify-between gap-4 font-mono">
          <span style={{ color: entry.color }}>{entry.name}</span>
          <span className="text-text">{Number(entry.value).toFixed(2)}</span>
        </div>
      ))}
    </div>
  );
}

export function CapabilityValueChart() {
  return (
    <div className="surface-card p-4 sm:p-5">
      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={capabilityCurves.curves} margin={{ top: 8, right: 16, bottom: 16, left: -10 }}>
            <CartesianGrid stroke="var(--color-grid-line)" vertical={false} />
            <XAxis
              dataKey="capability"
              type="number"
              domain={[0.1, 0.9]}
              ticks={[0.1, 0.3, 0.5, 0.7, 0.9]}
              tick={{ fill: '#727c86', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-subtle)' }}
              label={{ value: 'model capability →', position: 'insideBottom', offset: -8, fill: '#727c86', fontSize: 11 }}
            />
            <YAxis
              domain={[0, 0.8]}
              ticks={[0, 0.2, 0.4, 0.6, 0.8]}
              tickFormatter={(value: number) => value.toFixed(1)}
              tick={{ fill: '#727c86', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-subtle)' }}
              width={40}
            />
            <Tooltip content={<CapabilityTooltip />} />
            {SERIES.map((series) => (
              <Line
                key={series.key}
                type="monotone"
                dataKey={series.key}
                name={series.name}
                stroke={series.color}
                strokeWidth={2}
                dot={{ r: 3, fill: series.color, strokeWidth: 0 }}
                activeDot={{ r: 4 }}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5">
        {SERIES.map((series) => (
          <span key={series.key} className="flex items-center gap-2 font-mono text-[11px] text-text-muted">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: series.color }} />
            {series.name}
          </span>
        ))}
      </div>
    </div>
  );
}
