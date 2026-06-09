export function SiteFooter() {
  return (
    <footer className="border-t border-border-subtle">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <p className="font-mono text-xs text-text-faint">
          Will Lewis{' · '}
          <a
            href="https://wxl3.com"
            target="_blank"
            rel="noreferrer noopener"
            className="focus-ring text-text-muted underline-offset-2 transition hover:text-accent-muted hover:underline"
          >
            wxl3.com
          </a>
          {' · '}
          <a
            href="https://www.linkedin.com/in/willlinkedin/"
            target="_blank"
            rel="noreferrer noopener"
            className="focus-ring text-text-muted underline-offset-2 transition hover:text-accent-muted hover:underline"
          >
            linkedin.com/in/willlinkedin/
          </a>
          {' · '}
          <a
            href="https://github.com/willlewis"
            target="_blank"
            rel="noreferrer noopener"
            className="focus-ring text-text-muted underline-offset-2 transition hover:text-accent-muted hover:underline"
          >
            github.com/willlewis
          </a>
        </p>
      </div>
    </footer>
  );
}
