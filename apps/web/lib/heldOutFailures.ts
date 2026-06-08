// The REAL failure shapes the cockpit cards exhibit, derived from the worst-passing
// held-out items at the Sonnet / baseline tier (and weaker models). Every one of these
// clears the visible suite — they only fail the harness's held-out battery, which is the
// whole point. This is a static list owned by the web app, deliberately decoupled from
// data/failure_clusters.json (that file remains a seeded fixture for the Python suite).

export type HeldOutFailure = {
  /** Stable id for selection/keys. */
  id: string;
  /** Short shape name. */
  label: string;
  /** Which cockpit card it shows up in. */
  card: string;
  /** Where in the model tier it bites. */
  tier: string;
  severity: 'high' | 'medium' | 'low';
  /** One-sentence description of the shape. */
  pattern: string;
  /** Which held-out items expose it (and how it looks vs. the visible suite). */
  detectionRule: string;
  /** Held-out item names that fail when this shape occurs. */
  heldOutItems: string[];
  /** What a harness that catches it should do. */
  recommendedHarnessChange: string;
};

export const heldOutFailures: HeldOutFailure[] = [
  {
    id: 'missed_malformed_delimiter',
    label: 'Missed malformed-delimiter cases',
    card: 'A · Strip both comment styles',
    tier: 'GPT-5.4-nano → Haiku 4.5 (Sonnet 4.6 clears it)',
    severity: 'high',
    pattern:
      'Strips well-formed comments but mishandles unterminated block delimiters — an opened /* with no closing */, an unterminated block after a valid one, or a whole file that is one unterminated block.',
    detectionRule:
      'Held-out items unterminated_block, unterminated_after_valid and unterminated_whole fail while the visible suite and every well-formed block/line case pass.',
    heldOutItems: ['unterminated_block', 'unterminated_after_valid', 'unterminated_whole'],
    recommendedHarnessChange:
      'Score every run against a held-out battery that includes malformed and adversarial delimiter inputs the agent never sees, so conjunctive completeness — not just the happy path — decides the verdict.'
  },
  {
    id: 'broke_legacy_caller',
    label: 'Broke the legacy caller',
    card: 'B · customer_id → account_id migration',
    tier: 'down to Sonnet 4.6 (only Opus 4.8 preserves it)',
    severity: 'high',
    pattern:
      'Renames customer_id → account_id everywhere it can see, but the existing CLI caller still passes the old keyword and breaks — the migration looks done in the touched files; the untouched call site is what fails.',
    detectionRule:
      'Held-out item cli_caller_preserved fails — the legacy caller no longer runs after the rename — while the visible suite passes.',
    heldOutItems: ['cli_caller_preserved'],
    recommendedHarnessChange:
      'Hold out a whole-repo back-compat suite that exercises pre-existing callers, so a rename that breaks an untouched call site is rejected rather than scored as success.'
  },
  {
    id: 'narrowed_the_parser',
    label: 'Narrowed the parser',
    card: 'B · customer_id → account_id migration',
    tier: 'down to Sonnet 4.6 (only Opus 4.8 keeps cus_)',
    severity: 'high',
    pattern:
      'Switches the parser to the new account_ identifiers but drops back-compat for legacy cus_ ids — the parser now rejects inputs it used to accept. A forward-only migration that quietly narrows the accepted set.',
    detectionRule:
      'Held-out item account_parser_accepts_legacy fails — legacy cus_ identifiers are no longer accepted — while re-exports and the visible suite pass.',
    heldOutItems: ['account_parser_accepts_legacy'],
    recommendedHarnessChange:
      'Add held-out cases that feed legacy identifiers through the new parser, so dropping back-compat is caught instead of passing the forward-only happy path.'
  },
  {
    id: 'left_latent_defects',
    label: 'Left neighbouring latent defects',
    card: 'C · Fix split_bill + review the module',
    tier: 'every tier, incl. Opus 4.8 (tax_negative unfixed)',
    severity: 'medium',
    pattern:
      'Fixes the requested split_bill bug but leaves the rest of the module untouched — negative tax amounts, negative formatting, and messy-input parsing all stay broken. The asked-for fix lands; the review the task also asked for does not.',
    detectionRule:
      'Held-out items tax_negative, format_negative and parse_messy fail — neighbouring defects in the same module went unreviewed — while split_zero and the visible suite pass.',
    heldOutItems: ['tax_negative', 'format_negative', 'parse_messy'],
    recommendedHarnessChange:
      'Score the whole module, not just the named bug: a held-out battery over neighbouring functions turns "fixed the one thing" into "reviewed the module", which is what the task actually asked for.'
  }
];
