// Visible suite mirror (the executed copy is dateParser.test.js). Display only.
import { normalizeTimezoneOffset } from '../src/dateParser';

if (normalizeTimezoneOffset('2026-06-04T00:00:00+05:30') !== '2026-06-04T00:00:00+0530') {
  throw new Error('Expected +05:30 to normalize to +0530.');
}
