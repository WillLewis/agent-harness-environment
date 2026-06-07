// Visible suite — the agent may read and run this via `npm test`. It imports the
// real source (so a src edit changes the outcome) and asserts the single
// positive-offset case the agent can see.
const assert = require('assert');
const { normalizeTimezoneOffset } = require('../src/dateParser.js');

assert.strictEqual(
  normalizeTimezoneOffset('2026-06-04T00:00:00+05:30'),
  '2026-06-04T00:00:00+0530',
  'Expected +05:30 to normalize to +0530.'
);

console.log('PASS tests/dateParser.test.js');
