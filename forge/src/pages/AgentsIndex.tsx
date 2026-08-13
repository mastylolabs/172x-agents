import { useMemo, useState, useEffect } from 'react'
import { useSearchParams } from 'react-router'
import { Container, PageHeading } from '../components/Container'
import SearchBar from '../components/SearchBar'
import DomainTabs from '../components/DomainTabs'
import AgentCard from '../components/AgentCard'
import Breadcrumb from '../components/Breadcrumb'
import { agents } from '../data/agents'

export default function AgentsIndex() {
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')

  useEffect(() => {
    setQuery(params.get('q') ?? '')
  }, [params])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return agents
    return agents.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        a.summary.toLowerCase().includes(q) ||
        a.useWhen.toLowerCase().includes(q) ||
        a.domain.includes(q),
    )
  }, [query])

  const onSearch = (v: string) => {
    setQuery(v)
    if (v) setParams({ q: v }, { replace: true })
    else setParams({}, { replace: true })
  }

  return (
    <Container className="py-10">
      <Breadcrumb items={[{ label: 'Forge', to: '/' }, { label: 'Agents' }]} />
      <div className="mt-5">
        <PageHeading
          eyebrow="The library"
          title="Agents"
          description="A curated set of composable specialists. Every agent is reviewed, scoped, and honest about what it does — and what it leaves to a human."
        />
      </div>

      <div className="mt-8 space-y-5">
        <SearchBar value={query} onChange={onSearch} size="md" />
        <DomainTabs />
      </div>

      <p className="mt-8 text-[13px] text-muted-foreground">
        {filtered.length} {filtered.length === 1 ? 'agent' : 'agents'}
        {query && <> matching “{query}”</>}
      </p>

      {filtered.length === 0 ? (
        <EmptyState query={query} />
      ) : (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((a) => (
            <AgentCard key={a.slug} agent={a} />
          ))}
        </div>
      )}
    </Container>
  )
}

function EmptyState({ query }: { query: string }) {
  return (
    <div className="mt-6 rounded-[16px] border border-dashed border-border-strong bg-card/50 px-6 py-16 text-center">
      <p className="font-display text-[18px] font-bold text-foreground">
        No agents match “{query}”.
      </p>
      <p className="mt-2 text-[14px] text-muted-foreground">
        Try a broader term, or browse by domain above.
      </p>
    </div>
  )
}
