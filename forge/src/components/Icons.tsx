import type { SVGProps, ReactElement } from 'react'
import type { DomainSlug } from '../data/types'

type IconProps = SVGProps<SVGSVGElement>

const base = {
  width: 20,
  height: 20,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.6,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}

export function ProductIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 3 4 7.5v9L12 21l8-4.5v-9L12 3Z" />
      <path d="M4 7.5 12 12l8-4.5M12 12v9" />
    </svg>
  )
}

export function DesignIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="12" cy="12" r="9" />
      <circle cx="12" cy="12" r="3.2" />
      <path d="M12 3v3.8M12 17.2V21M3 12h3.8M17.2 12H21" />
    </svg>
  )
}

export function PlatformIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="3.5" y="4.5" width="17" height="6" rx="1.5" />
      <rect x="3.5" y="13.5" width="17" height="6" rx="1.5" />
      <path d="M7 7.5h.01M7 16.5h.01" />
    </svg>
  )
}

export function QualityIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M12 3 5 6v5c0 4.5 3 7.8 7 9 4-1.2 7-4.5 7-9V6l-7-3Z" />
      <path d="m9 11.5 2 2 4-4.5" />
    </svg>
  )
}

export function SecurityIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="5" y="10.5" width="14" height="9.5" rx="2" />
      <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5M12 14.5v2" />
    </svg>
  )
}

export const domainIcon: Record<DomainSlug, (p: IconProps) => ReactElement> = {
  product: ProductIcon,
  design: DesignIcon,
  platform: PlatformIcon,
  quality: QualityIcon,
  security: SecurityIcon,
}

export function SearchIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.2-3.2" />
    </svg>
  )
}

export function ArrowIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  )
}

export function CheckIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="m5 12.5 4.5 4.5L19 6.5" />
    </svg>
  )
}

export function CopyIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <rect x="9" y="9" width="11" height="11" rx="2" />
      <path d="M5 15V5a2 2 0 0 1 2-2h8" />
    </svg>
  )
}

export function EvidenceIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M8 3h6l4 4v14H6V5a2 2 0 0 1 2-2Z" />
      <path d="M13 3v4h4M9 13l2 2 3.5-3.5" />
    </svg>
  )
}

export function GateIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M4 20V5M20 20V5M4 8h16M4 13h16" />
      <path d="M9 8v5M15 8v5" />
    </svg>
  )
}
