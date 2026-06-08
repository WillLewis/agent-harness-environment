// Canonical executed source for the date_utils_hard toy task (CommonJS so `node`
// runs it with zero install). DEFAULT STATE IS BUGGY: the trailing timezone offset
// is returned unchanged.
//
// Spec — normalize the TRAILING timezone offset of an ISO-8601 timestamp to compact
// signed form (±HHMM), leaving the date and time component untouched:
//
//   "Z" or "z"           -> "+0000"
//   "±HH:MM"             -> "±HHMM"    (strip the colon)
//   "±HHMM"              -> "±HHMM"    (already compact; unchanged)
//   "±HH"                -> "±HH00"    (hour-only; pad the minutes)
//   no trailing offset   -> unchanged
//
// The time component's own colons must never be altered (e.g. "...T12:00:45" with no
// trailing offset stays exactly as-is, and "...T12:00:45.123+05:30" keeps the time).
//
// The visible test only pins the single "+05:30 -> +0530" case, so an incomplete fix
// (a ±HH:MM-only regex, a broad colon strip, or a hardcode) passes it. The harness
// held-out grammar suite is what actually decides correctness.
function normalizeTimezoneOffset(input) {
  return input; // BUG: returns input unchanged.
}

module.exports = { normalizeTimezoneOffset };
