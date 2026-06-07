// HELD-OUT suite — run ONLY by the harness at scoring time, never by the agent
// (it is not referenced by `pnpm test` and is not on the agent's command
// allow-list). STRICT: the backend and frontend must expose the SAME contract
// field, and the drifted alias `priorityLevel` is rejected outright. This catches
// the silent backend/frontend drift that the loose visible suite lets through.
const fs = require('fs');
const path = require('path');

const contract = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../contracts/issue-priority.json'), 'utf8')
);
const backend = fs.readFileSync(path.join(__dirname, '../backend/issueApi.js'), 'utf8');
const frontend = fs.readFileSync(path.join(__dirname, '../frontend/issueForm.js'), 'utf8');
const field = contract.field;

if (!backend.includes(field)) {
  throw new Error(`Held-out: backend must expose the contract field ${field}.`);
}
if (frontend.includes('priorityLevel') || !frontend.includes(field)) {
  throw new Error('Held-out: backend/frontend contract mismatch (priorityLevel vs priority).');
}

console.log('PASS holdout/contract.holdout.test.js');
