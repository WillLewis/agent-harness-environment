// TypeScript mirror of the executed source (src/dateParser.js) — kept for
// display realism; the runner executes the .js. DEFAULT STATE IS BUGGY: the
// trailing timezone offset colon is not normalized.
export function parseDate(input: string): Date {
  return new Date(input);
}

export function normalizeTimezoneOffset(input: string): string {
  return input; // BUG: returns input unchanged.
}

export function parseDateWithNormalizedOffset(input: string): Date {
  return new Date(normalizeTimezoneOffset(input));
}
