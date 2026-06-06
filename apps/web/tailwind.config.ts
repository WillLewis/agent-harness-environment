import type { Config } from 'tailwindcss';

// Make Tailwind opacity modifiers (e.g. `bg-success/15`, `ring-success/50`,
// `border-border/40`) work for colors defined as full CSS-variable values.
// Without this, the bare `var(--color-…)` form silently drops the opacity
// modifier and the utility is never generated, leaving tints transparent.
function alphaVar(varName: string): string {
  // Tailwind resolves color values that are functions at runtime, but the
  // exported `Config` color type only allows strings — cast to satisfy it.
  const resolver = ({ opacityValue }: { opacityValue?: string }) =>
    opacityValue === undefined
      ? `var(${varName})`
      : `color-mix(in oklab, var(${varName}) calc(${opacityValue} * 100%), transparent)`;
  return resolver as unknown as string;
}

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './lib/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['var(--font-mono)', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
        sans: ['var(--font-sans)', 'Inter', 'ui-sans-serif', 'system-ui']
      },
      colors: {
        page: alphaVar('--color-bg-page'),
        elevated: alphaVar('--color-bg-elevated'),
        surface: alphaVar('--color-surface'),
        'surface-2': alphaVar('--color-surface-2'),
        'surface-raised': alphaVar('--color-surface-raised'),
        border: alphaVar('--color-border'),
        'border-subtle': alphaVar('--color-border-subtle'),
        text: alphaVar('--color-text'),
        'text-muted': alphaVar('--color-text-muted'),
        'text-faint': alphaVar('--color-text-faint'),
        accent: {
          DEFAULT: alphaVar('--color-accent'),
          foreground: alphaVar('--color-accent-foreground'),
          muted: alphaVar('--color-accent-muted'),
          subtle: alphaVar('--color-accent-subtle')
        },
        success: alphaVar('--color-success'),
        warning: alphaVar('--color-warning'),
        danger: alphaVar('--color-danger'),
        info: alphaVar('--color-info'),
        assist: alphaVar('--color-assist'),
        code: {
          bg: alphaVar('--color-code-bg'),
          border: alphaVar('--color-code-border')
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
