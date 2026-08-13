import type { ReactNode } from 'react'

type Tone = 'default' | 'accent' | 'primary' | 'muted'

const tones: Record<Tone, string> = {
  default: 'border-border-strong bg-card text-muted-foreground',
  primary: 'border-primary/20 bg-primary/8 text-primary',
  accent: 'border-accent/30 bg-accent-soft text-accent-foreground',
  muted: 'border-border bg-muted text-muted-foreground',
}

export default function CapabilityBadge({
  children,
  tone = 'default',
  icon,
}: {
  children: ReactNode
  tone?: Tone
  icon?: ReactNode
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12px] font-medium leading-none tracking-tight ${tones[tone]}`}
    >
      {icon}
      {children}
    </span>
  )
}

// Maps a badge label to a tone for consistent styling across the app.
export function badgeTone(label: string): Tone {
  if (label === 'Evidence required') return 'accent'
  if (label === '172X Reviewed') return 'primary'
  return 'default'
}
