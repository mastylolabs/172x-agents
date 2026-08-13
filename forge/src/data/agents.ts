import catalog from './catalog.generated.json'
import type { Agent } from './types'

export const agents = catalog.agents as Agent[]

export const agentBySlug = Object.fromEntries(
  agents.map((agent) => [agent.slug, agent]),
) as Record<string, Agent>

export const agentsByDomain = (domain: string) =>
  agents.filter((agent) => agent.domain === domain)
