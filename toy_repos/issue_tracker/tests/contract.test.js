// VISIBLE suite — the agent may read and run this via `pnpm test`. It is LOOSE by
// design: it only checks that both sides mention the contract field name as a
// substring. A drifted frontend that ships `priorityLevel` still contains the
// substring "priority", so this naive check PASSES — the contract drift slips
// through. The harness-only strict held-out suite (holdout/contract.holdout.test.js)
// is what actually catches it.
const fs = require('fs');
const path = require('path');

const contract = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../contracts/issue-priority.json'), 'utf8')
);
const backend = fs.readFileSync(path.join(__dirname, '../backend/issueApi.js'), 'utf8');
const frontend = fs.readFileSync(path.join(__dirname, '../frontend/issueForm.js'), 'utf8');

if (!backend.includes(contract.field)) {
  throw new Error(`Backend API must expose the contract field ${contract.field}.`);
}
if (!frontend.includes(contract.field)) {
  throw new Error(`Frontend form must expose the contract field ${contract.field}.`);
}

console.log('PASS tests/contract.test.js');
