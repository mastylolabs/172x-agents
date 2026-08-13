import type { ReactNode } from 'react'

export function Container({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div className={`mx-auto max-w-[1280px] px-5 sm:px-8 ${className}`}>
      {children}
    </div>
  )
}

export function PageHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string
  title: string
  description?: string
}) {
  return (
    <div className="max-w-2xl">
      {eyebrow && (
        <div className="mb-2 font-mono text-[12px] uppercase tracking-[0.16em] text-accent">
          {eyebrow}
        </div>
      )}
      <h1 className="font-display text-[clamp(1.9rem,4vw,2.75rem)] font-extrabold leading-[1.05] tracking-tight text-foreground">
        {title}
      </h1>
      {description && (
        <p className="mt-3 text-[clamp(1rem,1.6vw,1.15rem)] leading-relaxed text-muted-foreground">
          {description}
        </p>
      )}
    </div>
  )
}
