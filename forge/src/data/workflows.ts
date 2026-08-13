import catalog from './catalog.generated.json'
import type { Workflow } from './types'

export const workflows = catalog.workflows as Workflow[]

export const workflowBySlug = Object.fromEntries(
  workflows.map((workflow) => [workflow.slug, workflow]),
) as Record<string, Workflow>
