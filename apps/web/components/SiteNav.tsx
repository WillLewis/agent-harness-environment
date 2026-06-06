const navLinks = [
  { href: '#premise', label: 'Why' },
  { href: '#protocol', label: 'Protocol' },
  { href: '#tasks', label: 'Tasks' },
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
      <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-x-3 gap-y-2 px-4 py-2.5 sm:flex-nowrap sm:gap-4 sm:px-6 sm:py-3 lg:px-8">
        <a
          href="#top"
          className="focus-ring shrink-0 rounded-md font-mono text-xs font-semibold tracking-tight text-text sm:text-sm"
        >
          AHE
        </a>

        <nav aria-label="Page sections" className="nav-scroll min-w-0 flex-1 overflow-x-auto">
          <ul className="flex w-max min-w-full items-center gap-0.5 sm:gap-1">
            {navLinks.map(({ href, label }) => (
              <li key={href} className="shrink-0">
                <a
                  href={href}
                  className="focus-ring inline-flex min-h-9 items-center rounded-md px-2.5 py-1.5 font-mono text-[11px] text-text-muted transition hover:text-text sm:px-3 sm:text-xs"
                >
                  {label}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <p
          className="hidden shrink-0 rounded-md border border-border-subtle bg-surface px-2 py-1 font-mono text-[9px] text-text-faint sm:block lg:hidden"
          aria-label="Hosted demo with precomputed traces"
        >
          Static demo
        </p>
        <p className="hidden shrink-0 rounded-md border border-border-subtle bg-surface px-2.5 py-1 font-mono text-[10px] text-text-faint lg:block">
          Hosted demo · precomputed traces
        </p>
      </div>
    </header>
  );
}
