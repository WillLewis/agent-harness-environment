import type { ReactNode } from 'react';

type SectionHeaderProps = {
  chapter?: string;
  label: string;
  title: string;
  description?: ReactNode;
  className?: string;
  titleId?: string;
};

export function SectionHeader({
  chapter,
  label,
  title,
  description,
  className = '',
  titleId
}: SectionHeaderProps) {
  return (
    <header className={className}>
      <p className="section-chapter">
        {chapter ? (
          <>
            <span className="text-text-muted">{chapter}</span>
            <span className="mx-2 text-text-muted">—</span>
          </>
        ) : null}
        <span className="section-label">{label}</span>
      </p>
      <h2 id={titleId} className="mt-2 text-2xl font-semibold tracking-tight text-text sm:text-3xl">
        {title}
      </h2>
      {description ? <div className="mt-3 max-w-3xl text-sm leading-relaxed text-text-muted">{description}</div> : null}
    </header>
  );
}
