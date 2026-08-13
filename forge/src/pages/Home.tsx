import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { Container } from '../components/Container'
import SearchBar from '../components/SearchBar'
import WorkflowCard from '../components/WorkflowCard'
import AgentCard from '../components/AgentCard'
import { domains } from '../data/domains'
import { agents, agentsByDomain } from '../data/agents'
import { workflows } from '../data/workflows'
import { domainIcon, ArrowIcon } from '../components/Icons'

const outcomes = [
  {
    title: 'Ship a safe change',
    copy: 'Move a risky change through gates to a protected-merge recommendation.',
    to: '/workflows/dev-loop',
  },
  {
    title: 'Make an architecture decision',
    copy: 'Get defensible boundaries, contracts, and a recorded rationale.',
    to: '/agents/principal-architect',
  },
  {
    title: 'Turn an idea into a build plan',
    copy: 'Go from a rough idea to a feasible, designed, buildable plan.',
    to: '/workflows/idea-to-build',
  },
  {
    title: 'Review a risky change',
    copy: 'Bring in independent QA, review, and security before you merge.',
    to: '/agents/security-reviewer',
  },
]

const steps = [
  {
    n: '01',
    title: 'Choose a specialist or workflow',
    copy: 'Browse a curated library by domain, outcome, or capability.',
  },
  {
    n: '02',
    title: 'Install 172X into your project',
    copy: 'One command adds selected Forge capabilities to your project.',
  },
  {
    n: '03',
    title: 'Work with clear evidence and human gates',
    copy: 'Every recommendation carries evidence; humans make the calls.',
  },
]

export default function Home() {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return null
    const a = agents.filter(
      (x) =>
        x.name.toLowerCase().includes(q) ||
        x.summary.toLowerCase().includes(q) ||
        x.useWhen.toLowerCase().includes(q),
    )
    const w = workflows.filter(
      (x) =>
        x.name.toLowerCase().includes(q) ||
        x.outcome.toLowerCase().includes(q),
    )
    return { a: a.slice(0, 4), w: w.slice(0, 2), total: a.length + w.length }
  }, [query])

  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-[0.5]"
          style={{
            backgroundImage:
              'radial-gradient(circle at center, rgba(18,86,74,0.10) 1px, transparent 1.4px)',
            backgroundSize: '22px 22px',
            maskImage:
              'radial-gradient(ellipse 80% 70% at 50% 0%, #000 30%, transparent 75%)',
            WebkitMaskImage:
              'radial-gradient(ellipse 80% 70% at 50% 0%, #000 30%, transparent 75%)',
          }}
        />
        <Container className="relative pb-14 pt-16 sm:pt-20">
          <div className="mx-auto max-w-3xl text-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-border-strong bg-card px-3 py-1.5 text-[12px] font-medium text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Curated · Open source · Human-in-the-loop
            </span>
            <h1 className="mt-6 font-display text-[clamp(2.3rem,6vw,4rem)] font-extrabold leading-[1.02] tracking-tight text-foreground">
              Forge the system behind
              <br className="hidden sm:block" /> your next build.
            </h1>
            <p className="mx-auto mt-5 max-w-xl text-[clamp(1.05rem,2vw,1.25rem)] leading-relaxed text-muted-foreground">
              Verified specialists and workflows for turning ideas into
              reviewable, shippable work.
            </p>
          </div>

          {/* Search */}
          <div className="mx-auto mt-9 max-w-2xl">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                navigate(`/agents?q=${encodeURIComponent(query)}`)
              }}
            >
              <SearchBar value={query} onChange={setQuery} />
            </form>

            {results && (
              <div className="mt-3 overflow-hidden rounded-2xl border border-border bg-card text-left shadow-[0_12px_40px_rgba(27,35,32,0.10)]">
                {results.total === 0 ? (
                  <p className="px-4 py-4 text-[14px] text-muted-foreground">
                    No matches for “{query}”.
                  </p>
                ) : (
                  <ul className="divide-y divide-border">
                    {results.w.map((w) => (
                      <li key={w.slug}>
                        <Link
                          to={`/workflows/${w.slug}`}
                          className="flex items-center justify-between gap-3 px-4 py-3 transition-colors hover:bg-muted/50"
                        >
                          <span>
                            <span className="mr-2 font-mono text-[11px] uppercase tracking-wide text-accent">
                              Workflow
                            </span>
                            <span className="text-[14px] font-medium text-foreground">
                              {w.name}
                            </span>
                          </span>
                          <ArrowIcon width={15} height={15} className="text-muted-foreground" />
                        </Link>
                      </li>
                    ))}
                    {results.a.map((a) => (
                      <li key={a.slug}>
                        <Link
                          to={`/agents/${a.slug}`}
                          className="flex items-center justify-between gap-3 px-4 py-3 transition-colors hover:bg-muted/50"
                        >
                          <span>
                            <span className="mr-2 font-mono text-[11px] uppercase tracking-wide text-primary">
                              Agent
                            </span>
                            <span className="text-[14px] font-medium text-foreground">
                              {a.name}
                            </span>
                          </span>
                          <ArrowIcon width={15} height={15} className="text-muted-foreground" />
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </Container>
      </section>

      {/* Outcome-first entry cards */}
      <Container className="py-14">
        <SectionLabel
          title="Start from an outcome"
          hint="Discovery should feel expansive; action should feel simple."
        />
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {outcomes.map((o) => (
            <Link
              key={o.title}
              to={o.to}
              className="group flex items-center justify-between gap-4 rounded-[16px] border border-border bg-card p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-[0_8px_24px_rgba(18,86,74,0.08)]"
            >
              <div>
                <h3 className="font-display text-[19px] font-bold tracking-tight text-foreground">
                  {o.title}
                </h3>
                <p className="mt-1.5 text-[14px] leading-relaxed text-muted-foreground">
                  {o.copy}
                </p>
              </div>
              <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border text-primary transition-colors group-hover:border-primary/40 group-hover:bg-primary/8">
                <ArrowIcon width={17} height={17} className="transition-transform group-hover:translate-x-0.5" />
              </span>
            </Link>
          ))}
        </div>
      </Container>

      {/* Featured workflows */}
      <Container className="py-6">
        <SectionLabel
          title="Featured workflows"
          action={{ to: '/workflows', label: 'All workflows' }}
        />
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          {workflows.slice(0, 2).map((w) => (
            <WorkflowCard key={w.slug} workflow={w} />
          ))}
        </div>
      </Container>

      {/* Browse by domain */}
      <Container className="py-14">
        <SectionLabel
          title="Browse by domain"
          action={{ to: '/agents', label: 'All agents' }}
        />
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {domains.map((d) => {
            const Icon = domainIcon[d.slug]
            const count = agentsByDomain(d.slug).length
            return (
              <Link
                key={d.slug}
                to={`/agents/${d.slug}`}
                className="group rounded-[16px] border border-border bg-card p-6 transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-[0_8px_24px_rgba(18,86,74,0.08)]"
              >
                <div className="flex items-center justify-between">
                  <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted text-primary transition-colors group-hover:border-primary/30 group-hover:bg-primary/8">
                    <Icon width={22} height={22} />
                  </span>
                  <span className="font-mono text-[12px] text-muted-foreground">
                    {count} {count === 1 ? 'agent' : 'agents'}
                  </span>
                </div>
                <h3 className="mt-4 font-display text-[19px] font-bold tracking-tight text-foreground">
                  {d.name}
                </h3>
                <p className="mt-1.5 text-[14px] leading-relaxed text-muted-foreground">
                  {d.tagline}
                </p>
              </Link>
            )
          })}
        </div>
      </Container>

      {/* How Forge works */}
      <section className="border-y border-border bg-card/50">
        <Container className="py-16">
          <SectionLabel title="How Forge works" />
          <div className="mt-8 grid gap-8 md:grid-cols-3">
            {steps.map((s, i) => (
              <div key={s.n} className="relative">
                <span className="font-mono text-[13px] font-semibold text-accent">
                  {s.n}
                </span>
                <h3 className="mt-2 font-display text-[18px] font-bold tracking-tight text-foreground">
                  {s.title}
                </h3>
                <p className="mt-1.5 text-[14px] leading-relaxed text-muted-foreground">
                  {s.copy}
                </p>
                {i < steps.length - 1 && (
                  <span
                    aria-hidden
                    className="absolute -right-4 top-1.5 hidden text-border-strong md:block"
                  >
                    →
                  </span>
                )}
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* Featured agents strip */}
      <Container className="py-14">
        <SectionLabel
          title="Recently reviewed specialists"
          action={{ to: '/agents', label: 'Browse all' }}
        />
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[agents[5], agents[3], agents[15]].map((a) => (
            <AgentCard key={a.slug} agent={a} />
          ))}
        </div>
      </Container>

      {/* Final install CTA */}
      <Container className="pb-20">
        <div className="overflow-hidden rounded-[20px] border border-primary/20 bg-primary/[0.04] px-6 py-12 text-center sm:px-12">
          <h2 className="font-display text-[clamp(1.6rem,3.5vw,2.4rem)] font-extrabold tracking-tight text-foreground">
            Ready to forge your next build?
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-[16px] leading-relaxed text-muted-foreground">
            Install 172X once, then add the specialists and workflows your
            project needs — with evidence and human gates built in.
          </p>
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/install"
              className="rounded-xl bg-primary px-6 py-3 text-[15px] font-semibold text-primary-foreground shadow-[0_2px_10px_rgba(18,86,74,0.25)] transition-colors hover:bg-primary-hover"
            >
              Install 172X
            </Link>
            <Link
              to="/compatibility"
              className="rounded-xl border border-border-strong bg-card px-6 py-3 text-[15px] font-semibold text-foreground transition-colors hover:border-primary/30 hover:text-primary"
            >
              View compatibility
            </Link>
          </div>
        </div>
      </Container>
    </>
  )
}

function SectionLabel({
  title,
  hint,
  action,
}: {
  title: string
  hint?: string
  action?: { to: string; label: string }
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="font-display text-[clamp(1.4rem,2.6vw,1.9rem)] font-extrabold tracking-tight text-foreground">
          {title}
        </h2>
        {hint && (
          <p className="mt-1 text-[14px] text-muted-foreground">{hint}</p>
        )}
      </div>
      {action && (
        <Link
          to={action.to}
          className="inline-flex items-center gap-1.5 text-[14px] font-semibold text-primary transition-colors hover:text-primary-hover"
        >
          {action.label}
          <ArrowIcon width={15} height={15} />
        </Link>
      )}
    </div>
  )
}
