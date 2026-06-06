const navLinks = [
  { href: '#premise', label: 'Why' },
  { href: '#protocol', label: 'Protocol' },
  { href: '#cockpit', label: 'Cockpit' },
  { href: '#evals', label: 'Evals' },
  { href: '#architecture', label: 'Architecture' }
] as const;

export function SiteNav() {
  return (
    <header
      className="sticky top-0 z-50 border-b border-border-subtle backdrop-blur-md"
      style={{ backgroundColor: 'var(--color-nav-bg)' }}
    >
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <a
          href="#top"
          className="focus-ring shrink-0 font-mono text-xs font-semibold tracking-tight text-text sm:text-sm"
        >
          AHE
        </a>

        <nav aria-label="Page sections" className="min-w-0 flex-1 overflow-x-auto">
          <ul className="flex items-center gap-1 sm:gap-2">
            {navLinks.map(({ href, label }) => (
              <li key={href} className="shrink-0">
                <a
                  href={href}
                  className="focus-ring rounded-md px-2.5 py-1.5 font-mono text-[11px] text-text-muted transition hover:text-text sm:text-xs"
                >
                  {label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <p className="hidden shrink-0 rounded-md border border-border-subtle bg-surface px-2.5 py-1 font-mono text-[10px] text-text-faint lg:block">
          Hosted demo · precomputed traces
        </p>
      </div>
    </header>
  );
}
