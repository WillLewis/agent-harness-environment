const fs = require('fs');
const path = require('path');

const contract = JSON.parse(
  fs.readFileSync(path.join(__dirname, '../contracts/issue-priority.json'), 'utf8')
);
const backend = fs.readFileSync(path.join(__dirname, '../backend/issueApi.js'), 'utf8');
const frontend = fs.readFileSync(path.join(__dirname, '../frontend/issueForm.js'), 'utf8');

if (!backend.includes(`priority`) || !backend.includes(contract.field)) {
  throw new Error('Backend API must expose the contract priority field.');
}

if (!frontend.includes(contract.field)) {
  throw new Error(`Frontend form must expose contract field ${contract.field}.`);
}

if (frontend.includes('priorityLevel')) {
  throw new Error('Frontend/backend contract mismatch: priorityLevel vs priority.');
}

console.log('PASS tests/contract.test.js');
