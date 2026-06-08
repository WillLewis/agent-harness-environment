'use client';

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
import { cardReliability, modelLabel, modelOrder } from '../lib/separationReliability';

// One line per card. Colors track the cockpit-card story: completeness, back-compat,
// latent-defect discovery. The capability axis is now the REAL model tier
// (nano → opus), not a synthetic 0.1..0.9 knob.
const CARD_COLOR: Record<string, string> = {
  completeness_comments_001: '#5bb0d7',
  compat_alias_migration_001: '#ea9344',
  latent_defects_001: '#9b8fc0'
};

function colorFor(taskId: string): string {
  return CARD_COLOR[taskId] ?? '#9aa7c2';
}

// Pivot the three cards into one row per model: { model, <taskId>: heldOut, ... }.
const chartData = modelOrder.map((model) => {
  const row: Record<string, number | string> = { model, modelLabel: modelLabel(model) };
  for (const card of cardReliability) {
    const point = card.models.find((p) => p.model === model);
    if (point) row[card.taskId] = point.heldOut;
  }
  return row;
});

const legend = cardReliability.map((card) => ({
  taskId: card.taskId,
  label: card.cardLabel,
  color: colorFor(card.taskId)
}));

type TooltipPayload = { dataKey: string; name: string; value: number; color: string };

function CapabilityTooltip({
  active,
  payload,
  label
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-border bg-elevated px-3 py-2 text-xs shadow-lg">
      <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-text-faint">{label}</div>
      <div className="mb-1 flex items-center justify-between gap-4 font-mono">
        <span className="text-text-faint">visible</span>
        <span className="text-text-faint">1.00</span>
      </div>
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
          <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 16, left: -10 }}>
            <CartesianGrid stroke="var(--color-grid-line)" vertical={false} />
            <XAxis
              dataKey="modelLabel"
              type="category"
              tick={{ fill: '#727c86', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-subtle)' }}
              label={{
                value: 'model tier (real) →',
                position: 'insideBottom',
                offset: -8,
                fill: '#727c86',
                fontSize: 11
              }}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={(value: number) => value.toFixed(1)}
              tick={{ fill: '#727c86', fontSize: 11 }}
              tickLine={false}
              axisLine={{ stroke: 'var(--color-border-subtle)' }}
              width={40}
            />
            {/* Visible suite is flat at 1.0 for every model — the reference the held-out lines fall below. */}
            <ReferenceLine
              y={1}
              stroke="#9aa7c2"
              strokeDasharray="4 4"
              label={{ value: 'visible = 1.0', position: 'insideTopRight', fill: '#9aa7c2', fontSize: 10 }}
            />
            <Tooltip content={<CapabilityTooltip />} />
            {legend.map((entry) => (
              <Line
                key={entry.taskId}
                type="monotone"
                dataKey={entry.taskId}
                name={entry.label}
                stroke={entry.color}
                strokeWidth={2}
                dot={{ r: 3, fill: entry.color, strokeWidth: 0 }}
                activeDot={{ r: 4 }}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5">
        {legend.map((entry) => (
          <span key={entry.taskId} className="flex items-center gap-2 font-mono text-[11px] text-text-muted">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: entry.color }} />
            {entry.label}
          </span>
        ))}
      </div>
      <p className="mt-4 max-w-3xl text-[11px] leading-relaxed text-text-faint">
        The capability axis is real models, not a synthetic knob: held-out mean-fraction per card climbs left → right
        across the tier (GPT-5.4-nano → Opus 4.8), while the visible suite stays pinned at 1.0 for every model. Latent-defect
        discovery is the steepest climb — even the frontier tier leaves items on the table.
      </p>
    </div>
  );
}
