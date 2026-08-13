export type DomainSlug =
  | 'product'
  | 'design'
  | 'platform'
  | 'quality'
  | 'security'

export interface Domain {
  slug: DomainSlug
  name: string
  tagline: string
  description: string
}

export interface Agent {
  slug: string
  name: string
  domain: DomainSlug
  kind: 'Specialist'
  summary: string // one sentence
  useWhen: string
  badges: string[] // capability badges
  reviewed: boolean
  evidenceRequired: boolean
  // detail sections
  receive: string[]
  qualityBar: string[]
  evidence: string[]
  boundaries: string[]
  workflows: string[] // workflow slugs used in
  version: string
}

export interface WorkflowAgentRef {
  slug: string
  role: string
}

export interface Workflow {
  slug: string
  name: string
  outcome: string
  summary: string
  steps: string[]
  gates: string[]
  agents: string[] // agent slugs
  version: string
}
