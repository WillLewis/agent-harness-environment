function normalizeTimezoneOffset(input) {
  return input.replace(/([+-]\d{2}):(\d{2})$/, '$1$2');
}
function parseDateWithNormalizedOffset(input) {
  return new Date(normalizeTimezoneOffset(input));
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
const parsed = parseDateWithNormalizedOffset('2026-06-04T00:00:00+05:30');
assert(!Number.isNaN(parsed.getTime()), 'Expected offset +05:30 to parse correctly.');
const negative = parseDateWithNormalizedOffset('2026-06-04T00:00:00-04:00');
assert(!Number.isNaN(negative.getTime()), 'Expected offset -04:00 to parse correctly.');
console.log('PASS tests/dateParser.test.js');
