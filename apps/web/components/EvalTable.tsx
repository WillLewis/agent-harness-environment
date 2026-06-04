import { policyComparison } from '../lib/demoData';

export function EvalTable() {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03]">
      <div className="border-b border-white/10 p-5">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Policy comparison · synthetic fixture</p>
        <h3 className="mt-2 text-2xl font-semibold text-white">Eval report</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="bg-white/[0.04] text-xs uppercase tracking-[0.18em] text-slate-400">
            <tr>
              <th className="px-5 py-4">Policy</th>
              <th className="px-5 py-4">Success</th>
              <th className="px-5 py-4">Recovery</th>
              <th className="px-5 py-4">Loop</th>
              <th className="px-5 py-4">Hallucinated files</th>
              <th className="px-5 py-4">Unsafe attempts</th>
              <th className="px-5 py-4">Human interventions</th>
              <th className="px-5 py-4">Cost</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {policyComparison.map((row) => (
              <tr key={row.policy} className="hover:bg-white/[0.03]">
                <td className="px-5 py-4 font-semibold text-white">{row.policy}</td>
                <td className="px-5 py-4 text-slate-300">{row.success}</td>
                <td className="px-5 py-4 text-slate-300">{row.recovery}</td>
                <td className="px-5 py-4 text-slate-300">{row.loop}</td>
                <td className="px-5 py-4 text-slate-300">{row.hallucinatedFiles}</td>
                <td className="px-5 py-4 text-slate-300">{row.unsafeAttempts}</td>
                <td className="px-5 py-4 text-slate-300">{row.humanInterventions}</td>
                <td className="px-5 py-4 text-slate-300">{row.cost}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
