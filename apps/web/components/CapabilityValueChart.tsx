'use client';

import clsx from 'clsx';
import { useState } from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import capabilityCurves from '../../../data/evals/capability_curves.json';

type Series = { key: string; label: string; kind: string };

// Productivity-primitive lines are muted; the durable integrity/safety exposure is
// amber/red (it rises with capability); a fading coordination exposure is muted too.
const KEY_COLOR: Record<string, string> = {
  testFirstLift: '#5bb0d7',
  contextFirstLift: '#9aa7c2'
};
const KIND_COLOR: Record<string, string> = {
  productivity: '#9aa7c2',
  integrity: '#ea9344', // rising spec-gaming exposure (warm = durable threat)
  safety: '#e0654f', // rising unsafe-attempt exposure (warm = durable threat)
  coordination: '#9b8fc0' // contract-drift exposure that FALLS (cool = fades, not durable)
};

function colorFor(series: Series): string {
  return KEY_COLOR[series.key] ?? KIND_COLOR[series.kind] ?? '#9aa7c2';
}

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
  const tasks = capabilityCurves.tasks;
  const [taskId, setTaskId] = useState(tasks[0]?.task_id);
  const task = tasks.find((row) => row.task_id === taskId) ?? tasks[0];
  const series = task.series as Series[];
  const [yMin, yMax] = task.yDomain as [number, number];

  return (
    <div className="surface-card p-4 sm:p-5">
      <div className="mb-4 flex flex-wrap gap-2">
        {tasks.map((row) => (
          <button
            key={row.task_id}
            type="button"
            onClick={() => setTaskId(row.task_id)}
            className={clsx(
              'rounded-full border px-3 py-1 text-xs font-medium transition',
              row.task_id === task.task_id
                ? 'border-border-strong bg-surface-2 text-text'
                : 'border-border-subtle text-text-muted hover:bg-surface-2/60'
            )}
          >
            {row.label}
          </button>
        ))}
      </div>

      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={task.curves} margin={{ top: 8, right: 16, bottom: 16, left: -10 }}>
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
              domain={[yMin, yMax]}
              tickFormatter={(value: number) => value.toFixed(1)}
              tick={{ fill: '#727c86', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-subtle)' }}
              width={40}
            />
            {yMin < 0 ? <ReferenceLine y={0} stroke="var(--color-border-subtle)" strokeDasharray="3 3" /> : null}
            <Tooltip content={<CapabilityTooltip />} />
            {series.map((entry) => (
              <Line
                key={entry.key}
                type="monotone"
                dataKey={entry.key}
                name={entry.label}
                stroke={colorFor(entry)}
                strokeWidth={2}
                dot={{ r: 3, fill: colorFor(entry), strokeWidth: 0 }}
                activeDot={{ r: 4 }}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5">
        {series.map((entry) => (
          <span key={entry.key} className="flex items-center gap-2 font-mono text-[11px] text-text-muted">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: colorFor(entry) }} />
            {entry.label}
          </span>
        ))}
      </div>
      <p className="mt-4 max-w-3xl text-[11px] leading-relaxed text-text-faint">{task.metric_note}</p>
    </div>
  );
}
