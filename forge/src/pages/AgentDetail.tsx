import { Link } from 'react-router'
import type { Agent } from '../data/types'
import { Container } from '../components/Container'
import Breadcrumb from '../components/Breadcrumb'
import InstallCard from '../components/InstallCard'
import CapabilityBadge, { badgeTone } from '../components/CapabilityBadge'
import { domainBySlug } from '../data/domains'
import { workflowBySlug } from '../data/workflows'
import { domainIcon, ArrowIcon, CheckIcon, EvidenceIcon } from '../components/Icons'

export default function AgentDetail({ agent }: { agent: Agent }) {
  const domain = domainBySlug[agent.domain]
  const Icon = domainIcon[agent.domain]
  const usedIn = agent.workflows
    .map((s) => workflowBySlug[s])
    .filter(Boolean)

  return (
    <>
      <Container className="py-10">
        <Breadcrumb
          items={[
            { label: 'Forge', to: '/' },
            { label: 'Agents', to: '/agents' },
            { label: domain.name, to: `/agents/${domain.slug}` },
            { label: agent.name },
          ]}
        />

        {/* Title block */}
        <div className="mt-6 flex items-start gap-4">
          <span className="inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-border bg-muted text-primary">
            <Icon width={26} height={26} />
          </span>
          <div>
            <h1 className="font-display text-[clamp(1.9rem,4vw,2.6rem)] font-extrabold leading-tight tracking-tight text-foreground">
              {agent.name}
            </h1>
            <p className="mt-2 max-w-2xl text-[clamp(1rem,1.6vw,1.15rem)] leading-relaxed text-muted-foreground">
              {agent.summary}
            </p>
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          <CapabilityBadge tone="primary">
            <Link to={`/agents/${domain.slug}`}>{domain.name}</Link>
          </CapabilityBadge>
          {agent.reviewed && (
            <CapabilityBadge tone="primary">172X Reviewed</CapabilityBadge>
          )}
          {agent.evidenceRequired && (
            <CapabilityBadge tone="accent" icon={<EvidenceIcon width={12} height={12} />}>
              Evidence required
            </CapabilityBadge>
          )}
          <CapabilityBadge tone="default" icon={<CheckIcon width={12} height={12} />}>
            Codex available
          </CapabilityBadge>
        </div>

        {/* Two-column layout */}
        <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_360px]">
          <div className="space-y-8">
            <Section title="Use when">
              <p className="text-[15px] leading-relaxed text-foreground/90">
                {agent.useWhen}
              </p>
            </Section>

            <Section title="What you receive">
              <BulletList items={agent.receive} check />
            </Section>

            <Section title="Quality bar">
              <BulletList items={agent.qualityBar} />
            </Section>

            <Section title="Evidence requirements">
              <BulletList items={agent.evidence} />
            </Section>

            <Section title="Boundaries">
              <BulletList items={agent.boundaries} muted />
            </Section>

            {usedIn.length > 0 && (
              <Section title="Used in workflows">
                <div className="grid gap-3 sm:grid-cols-2">
                  {usedIn.map((w) => (
                    <Link
                      key={w.slug}
                      to={`/workflows/${w.slug}`}
                      className="group flex items-center justify-between gap-3 rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/30"
                    >
                      <div>
                        <div className="font-display text-[15px] font-bold text-foreground">
                          {w.name}
                        </div>
                        <div className="mt-0.5 text-[13px] text-muted-foreground">
                          {w.outcome}
                        </div>
                      </div>
                      <ArrowIcon
                        width={16}
                        height={16}
                        className="shrink-0 text-primary transition-transform group-hover:translate-x-0.5"
                      />
                    </Link>
                  ))}
                </div>
              </Section>
            )}
          </div>

          {/* Sticky install card (desktop) */}
          <aside className="hidden lg:block">
            <div className="sticky top-24">
              <InstallCard agent={agent} />
            </div>
          </aside>

          {/* Install card inline (mobile/tablet) */}
          <div className="lg:hidden">
            <InstallCard agent={agent} />
          </div>
        </div>
      </Container>

      {/* Mobile sticky install CTA */}
      <div className="sticky bottom-0 z-40 border-t border-border bg-background/90 px-5 py-3 backdrop-blur-md lg:hidden">
        <a
          href="#main"
          className="flex items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 text-[15px] font-semibold text-primary-foreground"
          onClick={(e) => {
            e.preventDefault()
            window.scrollTo({ top: 0 })
          }}
        >
          Install {agent.name}
        </a>
      </div>
    </>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <section>
      <h2 className="font-display text-[13px] font-semibold uppercase tracking-[0.12em] text-accent">
        {title}
      </h2>
      <div className="mt-3">{children}</div>
    </section>
  )
}

function BulletList({
  items,
  check = false,
  muted = false,
}: {
  items: string[]
  check?: boolean
  muted?: boolean
}) {
  return (
    <ul className="space-y-2.5">
      {items.map((item) => (
        <li key={item} className="flex gap-3">
          {check ? (
            <CheckIcon
              width={17}
              height={17}
              className="mt-0.5 shrink-0 text-primary"
            />
          ) : (
            <span
              aria-hidden
              className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${
                muted ? 'bg-border-strong' : 'bg-accent'
              }`}
            />
          )}
          <span
            className={`text-[15px] leading-relaxed ${
              muted ? 'text-muted-foreground' : 'text-foreground/90'
            }`}
          >
            {item}
          </span>
        </li>
      ))}
    </ul>
  )
}
