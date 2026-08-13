import { useParams } from 'react-router'
import { domainBySlug } from '../data/domains'
import { agentBySlug } from '../data/agents'
import AgentCategory from './AgentCategory'
import AgentDetail from './AgentDetail'
import NotFound from './NotFound'

// A single /agents/:slug route resolves to a domain category page when the
// slug is a domain, otherwise to an individual agent detail page.
export default function AgentRoute() {
  const { slug = '' } = useParams()
  const domain = domainBySlug[slug]
  if (domain) return <AgentCategory domain={domain} />

  const agent = agentBySlug[slug]
  if (agent) return <AgentDetail agent={agent} />

  return <NotFound />
}
