import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agent Harness Environment',
  description: 'A flight recorder and evaluation environment for coding agents.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <a href="#cockpit" className="sr-only focus:not-sr-only focus-ring fixed left-4 top-4 z-[100] rounded-full bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950">
          Skip to cockpit
        </a>
        {children}
      </body>
    </html>
  );
}
