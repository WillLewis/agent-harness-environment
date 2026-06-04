import { parseDateWithNormalizedOffset } from '../src/dateParser';

function assert(condition: boolean, message: string) {
  if (!condition) throw new Error(message);
}

const parsed = parseDateWithNormalizedOffset('2026-06-04T00:00:00+05:30');
assert(!Number.isNaN(parsed.getTime()), 'Expected offset +05:30 to parse correctly.');

const negative = parseDateWithNormalizedOffset('2026-06-04T00:00:00-04:00');
assert(!Number.isNaN(negative.getTime()), 'Expected offset -04:00 to parse correctly.');
