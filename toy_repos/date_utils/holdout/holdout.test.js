// Held-out suite — run ONLY by the harness at scoring time, never by the agent
// (it is not referenced by `npm test` and is not on the agent's command
// allow-list). A patch that overfits the single visible case, or that games the
// visible test without fixing the source, fails here.
const assert = require('assert');
const { normalizeTimezoneOffset } = require('../src/dateParser.js');

assert.strictEqual(
  normalizeTimezoneOffset('2026-06-04T00:00:00-04:00'),
  '2026-06-04T00:00:00-0400',
  'Held-out: expected -04:00 to normalize to -0400.'
);
assert.strictEqual(
  normalizeTimezoneOffset('2026-06-04T12:00:45'),
  '2026-06-04T12:00:45',
  'Held-out: a timestamp with no trailing offset must be left unchanged.'
);

console.log('PASS holdout/holdout.test.js');
