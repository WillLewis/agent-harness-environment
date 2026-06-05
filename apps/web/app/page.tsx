import { Cockpit } from '../components/Cockpit';
import { EvalTable } from '../components/EvalTable';
import { ImplementationEvidence } from '../components/ImplementationEvidence';
import { routerDecision } from '../lib/demoData';

const protocolCards = [
  ['task_success', 'Whether the submitted patch passes target tests and expected behavior.'],
  ['recovery_rate', 'Whether the agent used new evidence after a failed command or test.'],
  ['hallucinated_file', 'A referenced file, symbol, script, or dependency that does not exist.'],
  ['loop_rate', 'Repeated tool calls or commands without new information.'],
  ['human_steering_burden', 'How many times the developer had to redirect the agent.'],
  ['unsafe_tool_attempt', 'A blocked shell, file, network, or secret-access action.']
];

export default function Home() {
  return (
    <main>
      <section className="relative overflow-hidden border-b border-white/10 px-4 py-24 sm:px-6 lg:px-8">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-cyan-200/80">Agent Harness Environment</p>
            <h1 className="mt-5 max-w-4xl text-5xl font-black tracking-tight text-white sm:text-7xl">A flight recorder for coding agents.</h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
              Evaluate how agents plan, use tools, recover from failed tests, avoid unsafe actions, and respond to developer steering.
            </p>
            <p className="mt-5 font-mono text-sm text-cyan-100">Same model. Same repo. Same task. Different harness. Different outcome.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a href="#cockpit" className="focus-ring rounded-full bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950">Replay the failure</a>
              <a href="#evals" className="focus-ring rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white">View eval report</a>
              <a href="#architecture" className="focus-ring rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white">Implementation map</a>
            </div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 shadow-2xl">
            <pre className="overflow-auto rounded-2xl bg-black/40 p-5 font-mono text-xs leading-6 text-slate-300">{`task: fix timezone parser regression\npolicy: baseline\nstep 04  TEST_FAIL     npm test -- dateParser\nstep 05  TEST_FAIL     repeated without evidence\nlabel    loop_detected\njudge    rejected\n\npolicy: guarded_recovery\nstep 03  READ_TEST     tests/dateParser.test.ts\nstep 04  READ_FILE     src/dateParser.ts\nstep 07  INSPECT_ERROR forced by harness\nstep 09  TEST_PASS     accepted`}</pre>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="max-w-3xl">
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">Premise</p>
          <h2 className="mt-3 text-3xl font-semibold text-white">When an agent fails, the product question is not only “was the model wrong?”</h2>
          <p className="mt-4 text-slate-300 leading-7">
            The harness determines whether the agent plans, reads files, edits code, runs commands, recovers from failure, asks for help, stops, or escalates.
          </p>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {protocolCards.map(([title, body]) => (
            <div key={title} className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
              <h3 className="font-mono text-sm text-cyan-100">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-400">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <Cockpit />

      <section id="evals" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <EvalTable />
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-cyan-200/80">RL-lite router</p>
            <h2 className="mt-3 text-3xl font-semibold text-white">Policy selection, not model training.</h2>
            <p className="mt-4 text-sm leading-7 text-slate-400">The router learns which harness policy fits each task class using eval outcomes as reward.</p>
            <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.03] p-5">
              <div className="font-mono text-sm text-slate-300">selected_policy: <span className="text-cyan-100">{routerDecision.selectedPolicy}</span></div>
              <p className="mt-3 text-sm text-slate-400">{routerDecision.why}</p>
            </div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            {routerDecision.expectedRewards.map(([policy, reward]) => (
              <div key={policy} className="mb-4 last:mb-0">
                <div className="mb-1 flex justify-between font-mono text-xs text-slate-400"><span>{policy}</span><span>{reward}</span></div>
                <div className="h-2 rounded-full bg-white/10"><div className="h-2 rounded-full bg-cyan-300" style={{ width: `${(reward / 5) * 100}%` }} /></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <ImplementationEvidence />
    </main>
  );
}
