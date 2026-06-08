import type { TaskId } from './cockpitTypes';

export type TaskStory = {
  setting: string;
  stakes: string;
  failurePlay: string;
  filesPlay: string;
  tagsPlay: string;
};

export const taskStories: Record<TaskId, TaskStory> = {
  completeness_comments_001: {
    setting:
      'A small utility, strip_comments, already removes # line comments from a snippet. A ticket asks to extend it so it also strips /* */ block comments. The repo ships exactly one new test: a clean block comment in the middle of a line.',
    stakes:
      'The function is reused across the codebase to sanitize user-pasted snippets. If it mishandles a malformed comment — an unterminated /* with no closing */ — it can either leak commented-out code downstream or strip the wrong span. "The one test is green" is not the same as "the parser is correct".',
    failurePlay:
      'A weaker model pattern-matches to the happy path: find /*, find the next */, cut everything between. The visible test passes immediately. But the held-out battery throws the ugly inputs at it — an unterminated block, an unterminated block right after a valid one, a comment that runs to the end of the string — and the naive scan walks off the end or stops early. Visible green, 9/12 held-out.',
    filesPlay:
      'The change set is tiny on purpose: core/comments.py and the single tests/test_block.py. That tightness is the trap — there is nothing in the visible suite to force the agent to consider malformed delimiters, so completeness has to come from the model reasoning about edge cases, not from the tests handing them over.',
    tagsPlay:
      'Tagged completeness because the failure is not a wrong answer — it is a partial one. The visible test certifies the easy case; the held-out battery is the only thing that distinguishes a model that enumerated the edge cases from one that stopped at the demo.'
  },
  compat_alias_migration_001: {
    setting:
      'Product is renaming the customer_id reference scheme to account_id. The parser, the package export, the invoice API, and a CLI importer all speak the old cus_ format today. The migration must flip everything to account_id while keeping the legacy cus_ callers working for one deprecation release.',
    stakes:
      'External integrations still send cus_ refs and an internal cli/importer.py still calls the old parser. Drop back-compat and the new account_id path looks perfect in the demo while every legacy caller silently breaks in production the moment the release ships.',
    failurePlay:
      'A mid-tier model does the obvious migration: rewrite core/refs to account_id, update the package export and the invoice API, run the visible test that only checks the new account_id path — all green. But it never re-points cli/importer.py and it makes the canonical parser reject legacy cus_ refs outright. The held-out battery checks exactly those two contracts and lands 4/6: account_parser_accepts_legacy and cli_caller_preserved both fail.',
    filesPlay:
      'expectedFiles span the whole blast radius: core/refs.py and core/__init__.py for the alias, api/invoices.py for the new path, and cli/importer.py — the legacy caller that is easy to forget because no visible test imports it. The held-out suite is what turns "I touched the files I was looking at" into "I kept every caller working".',
    tagsPlay:
      'Tagged migration and multi-file because the risk lives in the seam between surfaces, not in any single edit. A model that reads the legacy caller before editing keeps back-compat; one that only follows the new test drops it.'
  },
  latent_defects_001: {
    setting:
      'A bug report says split_bill drops a cent on uneven splits, and the module core/money.py is heading into a payments release. The ask is two-part: fix the reported bug, and review the rest of the module for anything else that looks wrong before it ships.',
    stakes:
      'Money code in a payments release is unforgiving. The named bug is the visible, easy half; the real value is the review half — neighbouring helpers (tax, formatting, parsing) carry their own latent defects on negative and messy inputs that no ticket has filed yet. Fix only what was reported and the release ships with known-shaped bugs still live.',
    failurePlay:
      'A model that treats this as a one-line bugfix patches split_bill, sees the single visible test go green, and stops. The held-out battery audits the whole module — negative tax, negative formatting, messy-input parsing, split-by-zero — and the unreviewed neighbours fail: 3/6 for a fix-only pass. A stronger model reviews the module and repairs most of them, but a single latent defect (negative tax) can still slip through at 5/6.',
    filesPlay:
      'The visible footprint is just core/money.py and tests/test_split.py, and that single test only exercises split_bill. Everything else in the module is invisible to the demo — the held-out battery is the only signal that separates "fixed the ticket" from "reviewed the module".',
    tagsPlay:
      'Tagged review because the graded outcome is discovery, not the reported repair. The visible test rewards fixing one thing; the held-out battery rewards looking at everything around it.'
  }
};
