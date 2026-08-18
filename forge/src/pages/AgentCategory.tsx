import { useMemo, useState } from 'react'
import { Container, PageHeading } from '../components/Container'
import SearchBar from '../components/SearchBar'
import DomainTabs from '../components/DomainTabs'
import FilterPanel from '../components/FilterPanel'
import AgentCard from '../components/AgentCard'
import Breadcrumb from '../components/Breadcrumb'
import { agentsByDomain } from '../data/agents'
import type { Domain } from '../data/types'

const PAGE_SIZE = 6

export default function AgentCategory({ domain }: { domain: Domain }) {
  const all = useMemo(() => agentsByDomain(domain.slug), [domain.slug])
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('All')
  const [visible, setVisible] = useState(PAGE_SIZE)

  const filterOptions = useMemo(() => {
    const kinds = Array.from(new Set(all.map((a) => a.kind)))
    return ['All', ...kinds]
  }, [all])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return all.filter((a) => {
      const matchesFilter = filter === 'All' || a.kind === filter
      const matchesQuery =
        !q ||
        a.name.toLowerCase().includes(q) ||
        a.summary.toLowerCase().includes(q) ||
        a.useWhen.toLowerCase().includes(q) ||
        a.doNotUseWhen.toLowerCase().includes(q)
      return matchesFilter && matchesQuery
    })
  }, [all, query, filter])

  const shown = filtered.slice(0, visible)

  return (
    <Container className="py-10">
      <Breadcrumb
        items={[
          { label: 'Forge', to: '/' },
          { label: 'Agents', to: '/agents' },
          { label: domain.name },
        ]}
      />
      <div className="mt-5">
        <PageHeading
          eyebrow="Domain"
          title={domain.name}
          description={domain.tagline}
        />
      </div>

      <div className="mt-8">
        <DomainTabs />
      </div>

      <div className="mt-6 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="lg:max-w-md lg:flex-1">
          <SearchBar
            value={query}
            onChange={(v) => {
              setQuery(v)
              setVisible(PAGE_SIZE)
            }}
            placeholder={`Search ${domain.name} agents…`}
            size="md"
          />
        </div>
        <FilterPanel
          options={filterOptions}
          active={filter}
          onChange={(v) => {
            setFilter(v)
            setVisible(PAGE_SIZE)
          }}
        />
      </div>

      {filtered.length === 0 ? (
        <div className="mt-8 rounded-[16px] border border-dashed border-border-strong bg-card/50 px-6 py-14 text-center">
          <p className="font-display text-[17px] font-bold text-foreground">
            Nothing here yet for that filter.
          </p>
          <p className="mt-1.5 text-[14px] text-muted-foreground">
            Adjust your search or choose “All”.
          </p>
        </div>
      ) : (
        <>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {shown.map((a) => (
              <AgentCard key={a.slug} agent={a} />
            ))}
          </div>
          {visible < filtered.length && (
            <div className="mt-8 flex justify-center">
              <button
                type="button"
                onClick={() => setVisible((v) => v + PAGE_SIZE)}
                className="rounded-xl border border-border-strong bg-card px-6 py-3 text-[14px] font-semibold text-foreground transition-colors hover:border-primary/30 hover:text-primary"
              >
                Show more agents
              </button>
            </div>
          )}
        </>
      )}
    </Container>
  )
}
