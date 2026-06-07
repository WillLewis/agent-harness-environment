// Canonical executed source for the date_utils toy task (CommonJS so `node` runs
// it with zero install). DEFAULT STATE IS BUGGY: the trailing timezone offset
// colon is not normalized, so colonized offsets like +05:30 are left unchanged.
// A correct fix strips the colon from the trailing ±HH:MM offset only — never
// from the time component.
function normalizeTimezoneOffset(input) {
  return input; // BUG: returns input unchanged.
}

module.exports = { normalizeTimezoneOffset };
