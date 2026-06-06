import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
        sans: ['var(--font-sans)', 'Inter', 'ui-sans-serif', 'system-ui']
      },
      colors: {
        page: 'var(--color-bg-page)',
        elevated: 'var(--color-bg-elevated)',
        surface: 'var(--color-surface)',
        'surface-2': 'var(--color-surface-2)',
        'surface-raised': 'var(--color-surface-raised)',
        border: 'var(--color-border)',
        'border-subtle': 'var(--color-border-subtle)',
        text: 'var(--color-text)',
        'text-muted': 'var(--color-text-muted)',
        'text-faint': 'var(--color-text-faint)',
        accent: {
          DEFAULT: 'var(--color-accent)',
          foreground: 'var(--color-accent-foreground)',
          muted: 'var(--color-accent-muted)',
          subtle: 'var(--color-accent-subtle)'
        },
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        danger: 'var(--color-danger)',
        info: 'var(--color-info)',
        assist: 'var(--color-assist)',
        code: {
          bg: 'var(--color-code-bg)',
          border: 'var(--color-code-border)'
        }
      },
      borderRadius: {
        card: '1rem',
        'card-lg': '1.25rem'
      }
    }
  },
  plugins: []
};

export default config;
