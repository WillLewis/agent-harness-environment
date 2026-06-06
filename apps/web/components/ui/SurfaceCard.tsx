import type { ReactNode } from 'react';
import clsx from 'clsx';

type SurfaceCardProps = {
  children: ReactNode;
  className?: string;
  raised?: boolean;
};

export function SurfaceCard({ children, className, raised = false }: SurfaceCardProps) {
  return (
    <div className={clsx(raised ? 'surface-card-raised' : 'surface-card', 'p-5', className)}>{children}</div>
  );
}
