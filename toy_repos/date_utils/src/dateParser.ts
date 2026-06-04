export function parseDate(input: string): Date {
  return new Date(input);
}

export function normalizeTimezoneOffset(input: string): string {
  return input.replace(/([+-]\d{2}):(\d{2})$/, '$1$2');
}

export function parseDateWithNormalizedOffset(input: string): Date {
  return new Date(normalizeTimezoneOffset(input));
}
