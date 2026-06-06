export function SiteFooter() {
  return (
    <footer className="border-t border-border-subtle">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <p className="font-mono text-xs text-text-faint">
          Agent Harness Environment · static hosted demo · no live LLM or runner in the browser
        </p>
        <p className="mt-2 text-xs leading-relaxed text-text-faint">
          Traces and eval cells are precomputed fixtures. Local runner, scorers, and MCP tools ship in-repo for
          development use.
        </p>
      </div>
    </footer>
  );
}
