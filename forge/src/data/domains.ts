import type { Domain } from './types'

export const domains: Domain[] = [
  {
    slug: 'product',
    name: 'Product',
    tagline: 'Turn intent into clear, testable direction.',
    description:
      'Frame problems, evidence demand, and shape specifications that engineering can defend.',
  },
  {
    slug: 'design',
    name: 'Design',
    tagline: 'Interfaces that are legible, humane, and buildable.',
    description:
      'Translate product intent into interaction and interface decisions with a clear rationale.',
  },
  {
    slug: 'platform',
    name: 'Platform',
    tagline: 'Design systems that can be built, tested, and defended.',
    description:
      'Set architecture, contracts, and implementation standards across the stack.',
  },
  {
    slug: 'quality',
    name: 'Quality',
    tagline: 'Independent review that protects the merge.',
    description:
      'Verify work against evidence before it reaches the main branch — never a rubber stamp.',
  },
  {
    slug: 'security',
    name: 'Security',
    tagline: 'Find the risk before it ships.',
    description:
      'Assess changes for exposure, misuse, and failure modes with concrete findings.',
  },
]

export const domainBySlug = Object.fromEntries(
  domains.map((d) => [d.slug, d]),
) as Record<string, Domain>
