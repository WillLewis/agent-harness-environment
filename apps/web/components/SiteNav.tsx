import { Github } from 'lucide-react';

const navLinks = [
  { href: '#premise', label: 'Why Harnesses Matter' },
  { href: '#tasks', label: 'Tasks' },
  { href: '#cockpit', label: 'Cockpit' },
  { href: '#evals', label: 'Evals' },
  { href: '#architecture', label: 'Architecture' }
] as const;

const GITHUB_URL = 'https://github.com';

export function SiteNav() {
  return (
    <header
      className="sticky top-0 z-50 border-b border-border-subtle backdrop-blur-md"
      style={{ backgroundColor: 'var(--color-nav-bg)' }}
    >
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <a
          href="#top"
          className="focus-ring flex shrink-0 items-center gap-2 rounded-md font-mono text-sm font-medium text-text"
        >
          <span className="size-2 rounded-sm bg-accent" aria-hidden="true" />
          agent-harness
        </a>

        <nav aria-label="Page sections" className="hidden items-center gap-0.5 md:flex">
          {navLinks.map(({ href, label }) => (
            <a
              key={href}
              href={href}
              className="focus-ring rounded-md px-3 py-1.5 text-sm text-text-muted transition hover:bg-surface-2 hover:text-text"
            >
              {label}
            </a>
          ))}
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            className="focus-ring ml-1 inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-sm text-text-muted transition hover:bg-surface-2 hover:text-text"
          >
            <Github className="size-4" aria-hidden="true" />
            GitHub
          </a>
        </nav>

        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer"
          className="focus-ring inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-xs text-text-muted transition hover:bg-surface-2 hover:text-text md:hidden"
          aria-label="View source on GitHub"
        >
          <Github className="size-4" aria-hidden="true" />
        </a>
      </div>
    </header>
  );
}
