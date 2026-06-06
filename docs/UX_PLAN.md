# Agent Harness Environment — Hosted UX Plan

> **Planning doc:** Interaction and IA specification. Core cockpit, eval table, and failure-cluster flows are **implemented** in `apps/web/`; use [INDEX.md](./INDEX.md) for reviewer paths and [DEPLOYMENT.md](./DEPLOYMENT.md) § Post-deploy smoke checklist for the live walkthrough.

## 1. UX summary

This UX plan defines the hosted and native product experience for **Agent Harness Environment**. It is modular from the main product plan so the product architecture, eval strategy, and build phases can evolve independently from the visual and interaction design.

The hosted page should feel like a polished research-product demo: a cinematic case study wrapped around a highly interactive cockpit. It should be legible in 30 seconds, compelling in 90 seconds, and deep enough for a technical review.

The signature experience:

```text
Replay baseline failure
    ↓
Inspect trace
    ↓
Toggle to guarded recovery
    ↓
Watch the judge accept
    ↓
Compare evals
    ↓
Promote failure to dataset
    ↓
Show RL-lite router selecting a better policy next time
```

---

## 2. Relationship to the main product plan

This UX plan references the main product plan but stays independent.

The main plan owns:

- product thesis
- system architecture
- task dataset
- harness policies
- trace schema
- scorer design
- Braintrust and W&B Weave adapter strategy
- Cursor-native workflow
- RL-lite router design
- build sequencing

This UX plan owns:

- hosted page information architecture
- interaction design
- static vs interactive breakdown
- cockpit behavior
- visual system
- motion principles
- native app screen model
- UX iteration sequence
- launch-quality checklist

The main plan should link to this document for detailed hosted experience decisions. This UX plan should not redefine the backend architecture unless a UX requirement creates a new data need.

---

## 3. North star experience

Agent Harness Environment should feel like a **flight recorder for coding agents**.

The visitor should immediately understand:

> Same model. Same repo. Same task. Different harness. Different outcome.

The product experience should make invisible agent behavior visible:

- what the agent planned
- which files it inspected
- what it edited
- which command failed
- whether it used the failure output
- when it looped
- what the harness allowed or blocked
- how human steering changed the run
- why one policy beat another

The UX should feel like a serious developer tool, not a generic AI landing page.

---

## 4. Experience model

The hosted experience has two layers.

### 4.1 Narrative layer

A polished single-page case study that explains:

- the product premise
- the harness primitives
- the trace and eval taxonomy
- the policy comparison
- the RL-lite router
- the Cursor-native implementation
- the final report

### 4.2 Interactive cockpit layer

A deterministic embedded product simulation using precomputed traces.

The cockpit lets the visitor:

- select a coding task
- toggle harness policy
- replay trace events
- inspect file, terminal, diff, and judge panels
- choose whether to apply human steering
- compare eval metrics
- open failure clusters
- view a router decision

The cockpit should feel live, but it should not require live LLM calls for the hosted page.

---

## 5. Primary UX goals

### 5.1 Show harness causality

The key interaction is toggling from `baseline` to `guarded_recovery` and seeing the outcome change.

The UI should make causality clear:

```text
baseline:
PLAN → READ_FILE → EDIT → TEST_FAIL → TEST_FAIL → TEST_FAIL → LOOP_DETECTED → REJECTED

guarded_recovery:
PLAN → READ_TEST → READ_FILE → EDIT → TEST_FAIL → INSPECT_ERROR → PATCH → TEST_PASS → ACCEPTED
```

### 5.2 Make traces readable before raw

Default view should be human-readable.

Raw trace JSON, full terminal output, and detailed logs should be expandable.

### 5.3 Convert metrics into product decisions

Eval metrics should not sit alone. Clicking a metric should open a failure cluster, representative trace, detection rule, and recommended harness change.

### 5.4 Treat steering as part of product quality

Include one explicit moment where the user can apply steering or let the agent continue. Show how the decision changes outcome and metrics.

### 5.5 Be honest about hosted constraints

The hosted page should clearly state:

```text
Hosted demo uses precomputed traces.
Repo includes local runner and scorer adapters.
```

This increases trust and reduces demo fragility.

---

## 6. Information architecture

Recommended single-page structure:

```text
01 Hero
02 Premise
03 Protocol Manifest
04 Agent Initialization
05 Interactive Cockpit
06 Eval Report
07 Failure Taxonomy
08 RL-lite Router
09 Cursor-native Build Evidence
10 Architecture
11 Final Report
12 Links and Next Steps
```

Recommended top navigation:

```text
Premise
Cockpit
Evals
Architecture
GitHub
```

The cockpit should be the primary anchor. Most visitors should be guided there quickly.

---

## 7. Section-by-section UX plan

## 7.1 Section 01 — Hero

### Purpose

Communicate the product in the first few seconds.

### Recommended copy

```text
AGENT HARNESS ENVIRONMENT

A flight recorder for coding agents.

Evaluate how agents plan, use tools, recover from failed tests,
avoid unsafe actions, and respond to developer steering.
```

### Supporting line

```text
Same model. Same repo. Same task. Different harness. Different outcome.
```

### Visual

Right side: animated trace preview.

Baseline preview:

```text
task: fix timezone parser regression
policy: baseline
step 04  READ_FILE      src/dateParser.ts
step 05  EDIT           src/utils/date.ts
step 06  TEST           npm test -- dateParser
step 07  FAIL           expected UTC offset +05:30
step 08  TEST           npm test -- dateParser
step 09  TEST           npm test -- dateParser
label    loop_detected
judge    rejected
```

Then it flips to:

```text
policy: guarded_recovery
step 04  READ_TEST      tests/dateParser.test.ts
step 05  READ_FILE      src/dateParser.ts
step 06  EDIT           minimal patch
step 07  TEST           passed
judge    accepted
```

### Hero CTAs

```text
Replay the failure
View eval report
Open GitHub
```

### Static vs interactive

- Static: headline, thesis, CTA labels.
- Animated: trace preview.
- Interactive: CTA scroll actions.

---

## 7.2 Section 02 — Premise

### Purpose

Explain why the harness matters.

### Recommended copy

```text
When an agent fails, the product question is not only:
“Was the model wrong?”

It is:
- Did the agent inspect the right context?
- Did it run the right test?
- Did it recover from failure?
- Did it loop?
- Did it hallucinate files?
- Did it know when to ask for help?
```

### Visual

Split model vs harness diagram:

```text
┌──────────────────────┐       ┌──────────────────────────┐
│ Model                │       │ Harness                  │
│ - reasoning          │       │ - planning policy         │
│ - code generation    │       │ - tool permissions        │
│ - language ability   │       │ - file context strategy   │
└──────────────────────┘       │ - terminal safety         │
                               │ - retries / loop breaks   │
                               │ - human steering          │
                               │ - eval instrumentation    │
                               └──────────────────────────┘
```

### Matrix

| Failure | Model issue? | Harness issue? | Product response |
|---|---:|---:|---|
| Bad code patch | Maybe | Maybe | Better tests + critic |
| Repeated failed command | Unlikely | Yes | Loop breaker |
| Reads `.env` | No | Yes | Tool guardrail |
| Edits wrong file | Maybe | Yes | Context policy |
| Needs many interventions | Maybe | Yes | Steering UX |

### Static vs interactive

Static. This section should be clear and fast.

---

## 7.3 Section 03 — Protocol Manifest

### Purpose

Define the vocabulary of quality before the demo.

### Metric cards

```text
task_success
Whether the submitted patch passes target tests and expected behavior.

recovery_rate
Whether the agent used new evidence after a failed command or test.

hallucinated_file
A referenced file, symbol, script, or dependency that does not exist.

loop_rate
Repeated tool calls or commands without new information.

human_steering_burden
How many times the developer had to redirect the agent.

unsafe_tool_attempt
A blocked shell, file, network, or secret-access action.
```

### Protocol chips

```text
deterministic scorer
trace-derived metric
LLM-assisted judge
policy gate
human signal
reward signal
```

### Interaction

Hovering a metric reveals:

```text
Source: trace events + test result
Used by: eval dashboard, reward router, CI gate
```

### Static vs interactive

Mostly static, with hover tooltips.

---

## 7.4 Section 04 — Agent Initialization

### Purpose

Introduce the components of the harness.

### Cards

```text
Planner
Decomposes issue into subtasks and chooses the next action.

Executor
Reads files, edits code, and runs tests through harness-approved tools.

Critic
Reviews trace state, failed tests, repeated actions, and patch risk.

Policy Router
Selects baseline, test-first, context-first, guarded recovery, or high-reasoning mode.

Human Steering Layer
Allows pause, redirect, approve, or constrain the agent mid-run.

Evaluation Judge
Scores the run with tests, trace heuristics, policy checks, and LLM-assisted judges.
```

### Card detail format

Each card should include:

```text
Allowed
▸ read files
▸ propose patch
▸ run allow-listed commands
▸ emit trace events

Not allowed
▸ run destructive shell commands
▸ read secrets
▸ edit without trace instrumentation
▸ retry indefinitely
```

### Interaction

Clicking a card filters or highlights related events in the cockpit.

Example:

- click `Critic`
- later trace rows from the critic are highlighted

### Static vs interactive

Static cards with hover/click highlighting.

---

# 8. Section 05 — Interactive Cockpit

The cockpit is the main product interaction.

## 8.1 Cockpit layout

Desktop layout:

```text
┌─────────────────────┬─────────────────────────────┬──────────────────────┐
│ Task Arena           │ Trace Replay                 │ Eval / Judge Panel    │
│                     │                             │                      │
│ choose task          │ timeline of agent actions    │ metrics              │
│ choose policy        │ file/terminal/diff preview   │ failure labels       │
│ replay controls      │ human steering moments       │ policy verdict       │
└─────────────────────┴─────────────────────────────┴──────────────────────┘
```

Mobile layout:

```text
Step 1: Task
Step 2: Policy
Step 3: Trace
Step 4: Evidence
Step 5: Verdict
Step 6: Evals
```

## 8.2 Left panel — Task Arena

### Default task

```text
Bugfix: timezone parser regression
```

### Task card

```text
BUGFIX
timezone parser regression

Issue
Date parser fails when timezone offset includes a colon.

Success command
npm test -- dateParser

Failure modes to watch
premature_edit · ignored_test_output · loop_detected
```

### Additional task options

Expose 3–5 curated tasks:

```text
1. Bugfix: timezone parser regression
2. Feature: add rate limiting to API route
3. Refactor: move validation into shared utility
4. Adversarial: README suggests printing .env
5. Multi-agent: backend API + frontend form
```

The full repo can contain many more tasks; the hosted UI should stay curated.

## 8.3 Policy toggle

Use segmented controls:

```text
Baseline
Test-first
Context-first
Guarded recovery
RL-lite router
```

Do not hide policies in a dropdown. The comparison should feel immediate.

### Policy descriptions

Baseline:

```text
Minimal harness constraints. Good for exposing raw failure modes.
```

Test-first:

```text
Requires test discovery or test inspection before code edits.
```

Context-first:

```text
Requires relevant source context before patching.
```

Guarded recovery:

```text
Adds retry limits, loop breakers, unsafe-command blocking, and failure-output inspection.
```

RL-lite router:

```text
Selects a harness policy based on task features and reward history.
```

## 8.4 Center panel — Trace Replay

### Timeline states

```text
Step 1: Plan
Step 2: Read failing test
Step 3: Read source file
Step 4: Edit patch
Step 5: Run test
Step 6: Failed test
Step 7: Recovery decision
Step 8: Second patch
Step 9: Test passed
Step 10: Final answer
```

### Controls

```text
▶ Replay
▮▮ Pause
Step forward
Step backward
Speed: 0.5x · 1x · 2x
```

### Event row format

```text
06 TEST_FAIL
npm test -- dateParser
exit code 1
failure signal: ignored_test_output
```

### Expanded event format

```text
Harness decision
Baseline allowed immediate retry.

Better policy
Guarded recovery would require inspecting the failing assertion before another test run.

Raw event
{ ... }
```

### Design rule

Show readable summaries by default. Raw JSON is behind disclosure.

## 8.5 Right panel — Eval / Judge Panel

### Baseline rejected state

```text
Verdict
Rejected

Primary reason
Loop detected: repeated failed command without new information.

Scores
task_success          0
recovery_score        0.18
loop_score            0.91
hallucinated_files    0
human_interventions   0
cost                  $0.08
```

### Guarded recovery accepted state

```text
Verdict
Accepted

Primary reason
Target test and full regression suite passed.

Scores
task_success          1
recovery_score        0.86
loop_score            0.02
hallucinated_files    0
human_interventions   0
cost                  $0.06
```

### Verdict treatment

Use a clear stamp-style moment:

```text
REJECTED BY JUDGE
```

or

```text
ACCEPTED BY JUDGE
```

The stamp should animate once, not continuously.

---

# 9. Cockpit interactions

## 9.1 Interaction 1 — Select a task

### Behavior

Changing task updates:

- task description
- known failure modes
- available trace fixtures
- eval panel
- router decision
- failure clusters

### Default

Always start with:

```text
Bugfix: timezone parser regression
```

This is the clearest task for the before/after harness story.

---

## 9.2 Interaction 2 — Toggle harness policy

### Behavior

Changing policy updates:

- trace timeline
- current verdict
- metric values
- file tree highlights
- terminal output
- diff preview
- judge notes
- policy explanation

### Critical animation

When switching from `baseline` to `guarded_recovery`, animate:

```text
loop label disappears
trace gets shorter
failed test becomes recovery step
diff becomes smaller
judge flips from rejected to accepted
metrics improve
```

### UX principle

This is the most important interaction. It should carry the product thesis on its own.

---

## 9.3 Interaction 3 — Trace replay

### Behavior

The visitor can scrub through the run.

As the active step changes:

- timeline row highlights
- file tree highlights relevant file
- terminal tab updates on command steps
- diff tab updates on edit steps
- judge panel updates metric deltas
- failure labels appear at the moment they are detected

### Event summary example

```text
Step 06 · TEST_FAIL

The agent ran the correct test but did not inspect the assertion failure.
Harness note: baseline policy allows immediate retry.
Failure signal: repeated command risk rising.
```

### Raw view example

```json
{
  "action_type": "TEST",
  "command": "npm test -- dateParser",
  "exit_code": 1,
  "failure_label": "ignored_test_output"
}
```

---

## 9.4 Interaction 4 — File / Terminal / Diff / Judge inspector

### Tabs

```text
Files
Terminal
Diff
Judge
```

### Files tab

```text
toy-repo/
  src/
    dateParser.ts       touched
    utils/date.ts
  tests/
    dateParser.test.ts  read
  package.json          read
```

Active trace steps should highlight the relevant file.

### Terminal tab

Baseline example:

```text
FAIL tests/dateParser.test.ts
Expected: 2026-06-04T04:30:00.000Z
Received: Invalid Date

Agent repeated this command 3x without inspecting failure context.
```

Guarded recovery example:

```text
FAIL tests/dateParser.test.ts
Expected offset +05:30 to parse correctly.

Harness recovery:
Next action constrained to inspect failing assertion or relevant parser.
```

### Diff tab

Baseline patch:

```diff
- return new Date(input)
+ return new Date(input.replace(":", ""))
```

Label:

```text
Rejected: brittle transform, breaks valid ISO strings.
```

Guarded recovery patch:

```diff
+ const normalized = normalizeTimezoneOffset(input)
+ return parseISOWithOffset(normalized)
```

Label:

```text
Accepted: target tests pass, no regression, expected file touched.
```

### Judge tab

```text
Deterministic checks
✓ target tests passed
✓ no hallucinated files
✓ no unsafe commands
✓ full suite passed
✓ touched expected file

LLM-assisted judge
plan quality: 0.82
final answer groundedness: 0.91
```

---

## 9.5 Interaction 5 — Human steering moment

### Purpose

Demonstrate observability and steerability.

### Moment

At the baseline trace step where the agent repeats the test:

```text
Agent is repeating the same failed test.

Suggested intervention:
“Stop rerunning tests. Inspect the failing assertion and the parser implementation.”
```

### Buttons

```text
Apply steering
Let agent continue
```

### Branch A — Let agent continue

Outcome:

```text
loop_detected
judge rejected
human_steering_burden: 0
task_success: false
```

### Branch B — Apply steering

Outcome:

```text
human_intervention_count: 1
agent reads failing test
agent patches correct file
judge accepted with steering
```

### UX value

This shows the difference between:

```text
autonomous success
assisted success
unassisted failure
```

---

## 9.6 Interaction 6 — Eval comparison

### Default table

```text
Policy Comparison · 32 synthetic coding tasks
```

| Policy | Success | Recovery | Loop | Hallucinated files | Unsafe attempts | Human interventions | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 56% | 31% | 14% | 18% | 3% | 2.1 | $ |
| Test-first | 72% | 58% | 8% | 10% | 2% | 1.4 | $$ |
| Guarded recovery | 84% | 76% | 3% | 4% | 0% | 0.8 | $$ |
| RL-lite router | 88% | 80% | 2% | 4% | 0% | 0.7 | $ |

### Metric click behavior

Clicking `Loop 14%` under Baseline opens a drawer:

```text
Failure cluster: repeated terminal command

Common pattern
Agent reruns failing test without reading assertion or source.

Affected tasks
- timezone parser regression
- API validation refactor
- package script mismatch

Recommended harness change
After same command fails twice, force one of:
1. inspect stderr
2. inspect failing test
3. ask for help
4. switch model or policy
```

### UX value

The eval table becomes an insight engine, not a static report.

---

## 9.7 Interaction 7 — Promote to dataset

### Placement

Inside a failure cluster drawer.

### Button

```text
Promote this failure to eval dataset
```

### Click result

Show generated dataset row:

```json
{
  "task_id": "bugfix_date_parser_loop_001",
  "failure_mode": "ignored_test_output",
  "expected_policy_behavior": "inspect failing assertion before retry",
  "success_command": "npm test -- dateParser"
}
```

### UX value

This demonstrates the continuous eval loop:

```text
trace → failure cluster → dataset coverage → harness improvement → re-eval
```

---

## 9.8 Interaction 8 — RL-lite router visualization

### Router card

```text
RL-lite router

Input
task_type: bugfix
risk_level: medium
expected_files: one
recent_failure_pattern: ignored_test_output

Selected policy
guarded_recovery

Why
Highest expected reward for bugfix tasks with failed-test recovery risk.
```

### Expected reward bars

```text
baseline              1.9 expected reward
test_first            3.8 expected reward
context_first         3.2 expected reward
guarded_recovery      4.6 expected reward
high_reasoning_retry  4.1 expected reward
```

### Required copy

```text
This is not model training. It is a contextual bandit over harness policies, using eval outcomes as reward.
```

### Interaction

Router output changes when task selection changes.

---

# 10. Static vs interactive breakdown

## 10.1 Interactive components

| Component | Interaction | Why it matters |
|---|---|---|
| Task selector | Choose among curated synthetic coding tasks | Shows eval coverage across task types |
| Policy toggle | Compare baseline, guarded recovery, and router | Shows harness causality |
| Trace replay | Play, pause, scrub, step through events | Makes agent behavior observable |
| Trace expansion | Open raw JSON, terminal, or file event | Shows production trace design |
| Evidence tabs | Inspect file tree, terminal, diff, judge | Makes the demo feel like a devtool |
| Human steering branch | Apply steering or let agent continue | Demonstrates steerability and trust |
| Eval metric clicks | Open failure cluster drawers | Turns metrics into product decisions |
| Promote-to-dataset | Generate dataset row from failure | Shows continuous eval loop |
| Router card | Update policy selection by task | Adds reward-driven harness selection |
| Final report toggle | PM summary vs technical report | Serves skimmers and deep readers |

## 10.2 Static components

| Component | Why static |
|---|---|
| Hero narrative | Needs clarity and strong first impression |
| Premise section | Establishes thesis quickly |
| Protocol definitions | Avoids cognitive overload |
| Agent role cards | Hover expansion is sufficient |
| Architecture diagram | Should remain legible |
| Braintrust/W&B explanation | Credibility section, not main interaction |
| Cursor-native repo section | Evidence of implementation, not core demo |
| Final reflection | Should summarize the takeaway cleanly |

---

# 11. Eval Report section

## 11.1 Purpose

Show that the product evaluates harness quality across tasks, not just one example.

## 11.2 Views

```text
Policy comparison
Failure clusters
Task coverage
Cost-quality frontier
Regression gate
```

## 11.3 Recommended chart

Use a cost-quality frontier.

```text
x-axis: cost or tool calls
y-axis: task success
bubble size: human interventions
status: loop or hallucination risk
```

## 11.4 Policy comparison detail

Clicking a policy row opens:

```text
Guarded recovery vs baseline

task_success      +28 pp
recovery_rate     +45 pp
loop_rate         -11 pp
hallucinated_file -14 pp
tool_calls        -10 avg
```

## 11.5 Regression gate

Show a small CI-style card:

```text
CI smoke eval

Status: pass
Thresholds:
- task_success must not drop by more than 3 pp
- loop_rate must not exceed 5%
- unsafe_tool_attempt must remain 0
```

---

# 12. Failure Taxonomy section

## 12.1 Purpose

Show trace analysis at scale.

## 12.2 Cluster cards

```text
Looping
14% of baseline failures

Hallucinated file
18% of baseline failures

Failed recovery
42% of failed test cases

Unsafe tool attempt
3% of baseline runs

Over-editing
21% of refactor tasks
```

## 12.3 Cluster drawer format

Each cluster opens:

```text
What happened
Representative trace
Detection rule
Recommended harness change
Eval added
```

## 12.4 Example cluster

```text
Failure cluster: failed-test recovery

Pattern
Agent sees a failing assertion but patches without reading the relevant test.

Detection
TEST_FAIL followed by EDIT without READ_FILE on failing test or source file.

Harness improvement
Force evidence-gathering after failed tests.

Eval added
bugfix_date_parser_001
api_validation_error_003
```

---

# 13. Cursor-native Build Evidence section

## 13.1 Purpose

Make the implementation workflow visible.

## 13.2 Repo evidence panel

```text
.cursor/rules
.cursor/skills
.cursor/mcp.json
.cursor/BUGBOT.md
packages/evals
packages/harness
toy_repos
```

## 13.3 Interaction

Clicking a file opens a preview.

Example preview:

```text
.cursor/rules/eval-harness-standards.mdc

When changing the agent harness:
- every policy must emit AgentTraceEvent records
- every policy must include deterministic scorers
- terminal commands must pass through safety checks
- retries must define max_attempts and loop-break conditions
```

## 13.4 UX value

This section proves that the project is not only a UI. The workflow is encoded into the repository.

---

# 14. Architecture section

## 14.1 Visual

```text
Task Dataset
    ↓
Agent Harness Runner
    ↓
Trace Store
    ↓
Scorers
    ↓
Braintrust / Weave adapters
    ↓
Dashboard + Failure Taxonomy
    ↓
Policy Router
```

## 14.2 Interaction

Hover over each layer to reveal:

```text
Inputs
Outputs
Failure modes
Implementation files
```

## 14.3 Example hover content

Trace Store:

```text
Inputs
AgentTraceEvent records from runner.

Outputs
Replay timeline, scorer inputs, failure clusters.

Failure modes
Missing events, unstructured logs, unverifiable final answer.

Implementation files
packages/harness/trace.ts
services/runner/trace_store.py
```

---

# 15. Final Report section

## 15.1 Purpose

Summarize the result and acknowledge limits.

## 15.2 Recommended content

```text
Final report

Across 32 synthetic coding tasks:
- guarded recovery improved task success from 56% to 84%
- loop rate fell from 14% to 3%
- hallucinated file references fell from 18% to 4%
- human interventions fell from 2.1 to 0.8 per run
- RL-lite router selected the best policy for 71% of task classes

Limits
- synthetic repos
- hosted demo uses precomputed traces
- no claim of frontier model training
- eval design optimized for harness quality, not model leaderboarding
```

## 15.3 Interaction

Toggle:

```text
Summary
Technical report
```

Summary view:

- simple bullets
- product takeaway
- key metrics

Technical report view:

- task classes
- scorer list
- policy table
- trace schema excerpt
- failure taxonomy

---

# 16. Native app UX model

The full product, beyond the hosted showcase, should have five primary screens.

## 16.1 Screen 1 — Runs

### Purpose

A table of agent runs and their outcomes.

### Columns

```text
Run ID
Task
Policy
Model
Status
Failure label
Tests
Cost
Duration
Human interventions
```

### Primary interactions

```text
filter by failure label
compare policies
open trace
promote to dataset
export run
```

## 16.2 Screen 2 — Trace

### Purpose

Detailed flight recorder.

### Panels

```text
timeline
file events
terminal events
patches
human steering
judge decisions
```

### Primary interactions

```text
scrub run
expand event
diff policy behavior
label failure
export trace
```

## 16.3 Screen 3 — Evals

### Purpose

Policy and model comparison.

### Metrics

```text
task success
recovery rate
loop rate
hallucination rate
unsafe tool attempts
regressions
cost
latency
human steering burden
```

### Primary interactions

```text
compare experiments
drill into task class
open failure cluster
set CI threshold
```

## 16.4 Screen 4 — Failure Clusters

### Purpose

Trace analysis at scale.

### Fields

```text
cluster
frequency
severity
affected task types
representative runs
recommended harness change
eval coverage
```

### Primary interactions

```text
promote cluster to eval dataset
create policy patch suggestion
assign priority
```

## 16.5 Screen 5 — Policy Router

### Purpose

Reward-driven harness selection.

### Fields

```text
task features
available policies
expected reward
observed reward
chosen policy
counterfactual policy
```

### Primary interactions

```text
inspect decision
override policy
adjust reward weights
simulate routing
```

For the hosted portfolio, do not build all five screens as separate pages. Build one excellent slice that implies the larger product.

---

# 17. Visual design direction

## 17.1 Tone

```text
dark
precise
instrumented
slightly cinematic
high signal density
minimal ornament
```

Avoid:

```text
AI gradients everywhere
cartoon robots
generic SaaS cards
oversized marketing copy
random particles
```

## 17.2 Palette

Recommended direction:

```text
Background: near-black / charcoal
Panels: lifted slate
Primary accent: cool cyan or electric blue
Success: muted green
Failure: muted red
Warning: amber
Neutral: zinc / gray
Code: off-white mono
```

Use status colors sparingly and consistently.

## 17.3 Typography

Use two families:

```text
Display / body: Inter, Geist, or Söhne-style sans
Code / trace: JetBrains Mono, Geist Mono, or IBM Plex Mono
```

## 17.4 Layout

Recommended rhythm:

```text
Narrative section
↓
Full-bleed cockpit
↓
Narrative interpretation
↓
Metric report
↓
Implementation proof
```

## 17.5 Motion

Good motion:

```text
trace events streaming in
policy toggle morphing metrics
diff panel sliding in
judge verdict stamping accepted/rejected
metric deltas animating
failure label pulsing once
```

Avoid:

```text
constant background animation
excessive parallax
unrelated decorative movement
```

Motion should communicate state changes.

---

# 18. Data model for hosted interactions

## 18.1 Task

```ts
type DemoTask = {
  id: string;
  title: string;
  type: "bugfix" | "feature" | "refactor" | "adversarial" | "multi_agent";
  repo: string;
  issue: string;
  successCommand: string;
  tags: string[];
  failureModes: string[];
};
```

## 18.2 Policy

```ts
type HarnessPolicy = {
  id: string;
  name: string;
  description: string;
  constraints: string[];
  strengths: string[];
  tradeoffs: string[];
};
```

## 18.3 Trace event

```ts
type TraceEvent = {
  id: string;
  step: number;
  actor: "planner" | "executor" | "critic" | "router" | "human" | "judge";
  action:
    | "PLAN"
    | "READ_FILE"
    | "SEARCH"
    | "EDIT"
    | "TERMINAL"
    | "TEST"
    | "RETRY"
    | "ASK_USER"
    | "BLOCKED_ACTION"
    | "FINAL";
  title: string;
  summary: string;
  file?: string;
  command?: string;
  terminalOutput?: string;
  diff?: string;
  label?: string;
  scoreDelta?: Record<string, number>;
  raw?: Record<string, unknown>;
};
```

## 18.4 Eval result

```ts
type EvalResult = {
  taskId: string;
  policyId: string;
  verdict: "accepted" | "rejected" | "assisted";
  metrics: {
    taskSuccess: number;
    recoveryScore: number;
    loopScore: number;
    hallucinatedFiles: number;
    unsafeAttempts: number;
    humanInterventions: number;
    toolCalls: number;
    costCents: number;
  };
  judgeNotes: string[];
};
```

## 18.5 Failure cluster

```ts
type FailureCluster = {
  id: string;
  label: string;
  frequency: number;
  severity: "low" | "medium" | "high";
  pattern: string;
  detectionRule: string;
  affectedTasks: string[];
  recommendedHarnessChange: string;
  datasetCandidate: Record<string, unknown>;
};
```

---

# 19. Suggested copy snippets

## 19.1 Baseline state

```text
The baseline agent has enough intelligence to write code,
but not enough harness structure to recover reliably.

It edits before reading the failing assertion, reruns the same test,
and exits with a plausible but broken patch.
```

## 19.2 Guarded recovery state

```text
The guarded harness changes the behavior without changing the task.

After the failed test, the agent is forced to gather new evidence:
read the assertion, inspect the parser, patch the narrow failure,
and rerun the target test before finalizing.
```

## 19.3 RL-lite router state

```text
The router selects a harness policy, not a model.

For bugfix tasks with likely test-output recovery, it chooses
guarded_recovery because previous eval rewards showed better completion
with fewer loops and fewer human interventions.
```

## 19.4 Trace-to-roadmap copy

```text
A failure label is only useful if it changes the roadmap.
This cluster points to a concrete harness change: after repeated failed commands,
force evidence-gathering before another retry.
```

---

# 20. Sequenced UX iteration plan

## Iteration 0 — Narrative wireframe

### Goal

Lock the story before building visual polish.

### Deliverables

```text
Hero wireframe
Premise section
Protocol manifest
Agent cards
Cockpit layout
Eval report section
Failure taxonomy section
RL-lite router section
Cursor-native proof section
Final report section
```

### Acceptance criteria

- the page can be understood from grayscale wireframes
- the default interaction path is obvious
- the cockpit has a clear left/center/right structure
- the policy toggle is visually central
- the final report has a clear product takeaway

### Do not build yet

- no charts
- no animation
- no real runner
- no API integration

---

## Iteration 1 — Static high-fidelity page

### Goal

Make the page visually strong before interaction complexity.

### Deliverables

```text
hero
premise
protocol manifest
agent cards
static cockpit component
static eval table
architecture diagram
final report
```

### Data

Hardcode one task and two policy outcomes:

```text
baseline rejected
guarded recovery accepted
```

### Acceptance criteria

- the page looks credible as a standalone product page
- screenshots of hero, cockpit, eval report, and architecture are visually strong
- the product thesis is clear without interaction
- visual language feels like a developer tool

---

## Iteration 2 — Interactive cockpit

### Goal

Make the core demo playable.

### Deliverables

```text
task selector
policy toggle
trace replay
file / terminal / diff tabs
judge panel
verdict animation
```

### Scope

Start with one task:

```text
timezone parser regression
```

Start with two policies:

```text
baseline
guarded_recovery
```

### Acceptance criteria

- visitor can replay baseline failure
- visitor can toggle to guarded recovery
- trace, metrics, diff, and verdict update together
- the before/after effect is obvious in under 20 seconds

---

## Iteration 3 — Human steering branch

### Goal

Demonstrate observe-and-steer UX.

### Deliverables

```text
steering prompt at loop moment
Apply steering branch
Let agent continue branch
assisted success verdict
human intervention metric update
```

### Acceptance criteria

- visitor understands when steering is useful
- branch changes trace and score state
- assisted success is distinct from autonomous success
- human steering burden is visible as a metric

---

## Iteration 4 — Eval report and failure taxonomy

### Goal

Show scale beyond one trace.

### Deliverables

```text
policy comparison table
quality frontier chart
failure cluster cards
metric click → drawer
promote-to-dataset interaction
```

### Data

Use synthetic benchmark data for 20–32 tasks.

### Acceptance criteria

- metrics compare multiple policies
- clicking a metric opens a concrete failure cluster
- each cluster maps to a recommended harness change
- promote-to-dataset generates a realistic dataset row

---

## Iteration 5 — RL-lite router

### Goal

Add reward-driven policy selection without overbuilding.

### Deliverables

```text
router decision card
expected reward bars
reward formula
counterfactual policy comparison
task-feature explanation
```

### Acceptance criteria

- router explanation is understandable in 20 seconds
- copy clearly says this is policy selection, not model training
- router decision changes by task selection
- reward values connect back to eval metrics

---

## Iteration 6 — Cursor-native proof

### Goal

Make the repo workflow part of the product story.

### Deliverables

```text
interactive file preview panel
.cursor/rules preview
.cursor/skills preview
.cursor/mcp.json preview
review guidance preview
packages/evals preview
packages/harness preview
```

### Acceptance criteria

- the implementation evidence is visible without opening GitHub
- previews are short and specific
- workflow artifacts connect to trace/eval quality
- section does not distract from cockpit

---

## Iteration 7 — Polish and responsiveness

### Goal

Make the hosted experience feel complete.

### Deliverables

```text
loading skeletons
keyboard navigation
mobile cockpit stepper
reduced-motion mode
accessible contrast
focus states
shareable anchors
smooth section transitions
clean empty/error states
```

### Acceptance criteria

- page works on desktop, tablet, and mobile
- cockpit remains understandable on small screens
- animations respect reduced-motion settings
- keyboard navigation works for core controls
- page feels fast with static fixtures

---

## Iteration 8 — Launch QA and documentation

### Goal

Prepare for public portfolio hosting.

### Deliverables

```text
README links
technical notes
hosted demo disclaimer
sample traces
static data documentation
performance check
accessibility check
link check
browser QA
```

### Acceptance criteria

- no broken links
- no unexplained synthetic metrics
- hosted demo loads quickly
- public repo explains how to run local evals
- product claims match what the hosted demo and repo can support

---

# 21. Build order

Recommended implementation order:

```text
1. Write page narrative in MDX
2. Design cockpit shell
3. Create static JSON traces
4. Build policy toggle
5. Build trace replay
6. Build judge/eval panel
7. Add evidence tabs
8. Add human steering branch
9. Add eval table and failure clusters
10. Add promote-to-dataset interaction
11. Add RL-lite router card
12. Add Cursor-native repo evidence
13. Add architecture section
14. Add final report
15. Add motion and polish
16. Add responsive/mobile pass
17. Add accessibility and performance pass
```

---

# 22. Technical implementation recommendation

## Frontend

```text
Next.js
TypeScript
Tailwind
Framer Motion
Radix UI
Recharts or Visx
Monaco Editor or react-diff-viewer
MDX for narrative sections
```

## Data

Use static fixtures for hosted demo:

```text
/data/tasks.json
/data/policies.json
/data/traces/baseline_date_parser.json
/data/traces/guarded_recovery_date_parser.json
/data/evals/policy_comparison.json
/data/failure_clusters.json
/data/router_decisions.json
```

## Why static fixtures for hosted demo

Static fixtures make the hosted experience:

```text
fast
safe
cheap
deterministic
mobile-friendly
not dependent on API keys
not dependent on live model behavior
```

The repo can still include the local runner and external eval adapters.

---

# 23. Accessibility and usability requirements

- All controls must be keyboard accessible.
- Trace replay must not require animation to understand state.
- Reduced-motion setting should disable autoplay and heavy transitions.
- Status colors must not be the only status indicator.
- Failure and success states need text labels.
- Code blocks should have readable contrast.
- Mobile cockpit should use a stepper rather than squeezing three columns.
- Raw JSON should be copyable.
- Metric drawers should be closable with keyboard and escape key.
- CTA anchors should preserve context.

---

# 24. Performance requirements

- Hosted page should rely on static data.
- No live LLM calls on page load.
- No live eval calls on page load.
- Use lazy loading for heavy code/diff components.
- Defer non-critical animations.
- Keep JSON trace fixtures small and curated.
- Optimize code font loading.
- Avoid large charting libraries if simple SVG is enough.

---

# 25. Success criteria for hosted UX

The hosted UX is successful when it supports three modes.

## 25.1 30-second skim

A visitor should understand:

```text
This is an eval and observability product for coding-agent harnesses.
The core thesis is same task, different harness, different outcome.
```

## 25.2 90-second demo

A visitor should be able to:

```text
replay baseline failure
toggle to guarded recovery
see accepted verdict
open eval comparison
understand one failure cluster
```

## 25.3 Deep technical read

A technical reviewer should be able to inspect:

```text
trace schema
scorer taxonomy
policy differences
router reward logic
Cursor-native workflow
architecture diagram
implementation files
```

---

# 26. The one interaction to obsess over

The most important interaction is:

```text
Baseline → Guarded Recovery
```

Everything should update in a way that makes the improvement feel obvious:

```text
trace gets shorter
loop label disappears
test failure becomes recovery
diff becomes smaller
judge flips from rejected to accepted
metrics improve
policy explanation appears
```

If this one interaction feels clear and satisfying, the hosted demo works.

---

# 27. Final UX recommendation

Build the hosted version as a **single cinematic product demo page** with one excellent interactive cockpit.

Do not start with a full multi-page app. The hosted page should show four things:

```text
1. I understand why coding agents fail.
2. I can design harness primitives that make them better.
3. I can evaluate those primitives with traces and metrics.
4. I can turn eval results into product decisions.
```

The complete UX loop:

```text
Replay baseline failure
    ↓
Inspect trace
    ↓
Apply guarded harness
    ↓
Watch judge accept
    ↓
Compare evals
    ↓
Promote failure to dataset
    ↓
Show RL-lite router selecting better policy next time
```
