import type { Metadata } from 'next';
import { SiteFooter } from '../components/SiteFooter';
import { SiteNav } from '../components/SiteNav';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agent Harness Environment',
  description: 'A flight recorder and evaluation environment for coding agents.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="page-grid-bg">
        <a
          href="#cockpit"
          className="sr-only focus:not-sr-only focus-ring fixed left-4 top-4 z-[100] rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground"
        >
          Skip to cockpit
        </a>
        <SiteNav />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
