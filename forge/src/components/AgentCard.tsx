import { Link } from 'react-router'
import type { Agent } from '../data/types'
import { domainIcon, ArrowIcon, EvidenceIcon } from './Icons'
import CapabilityBadge, { badgeTone } from './CapabilityBadge'

export default function AgentCard({ agent }: { agent: Agent }) {
  const Icon = domainIcon[agent.domain]
  return (
    <Link
      to={`/agents/${agent.slug}`}
      className="group flex h-full flex-col rounded-[16px] border border-border bg-card p-5 shadow-[0_1px_2px_rgba(27,35,32,0.04)] transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-[0_8px_24px_rgba(18,86,74,0.08)]"
    >
      <div className="mb-4 flex items-start justify-between">
        <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-muted text-primary transition-colors group-hover:border-primary/30 group-hover:bg-primary/8">
          <Icon width={20} height={20} />
        </span>
        <span className="font-mono text-[11px] uppercase tracking-[0.1em] text-muted-foreground">
          Specialist
        </span>
      </div>

      <h3 className="font-display text-[17px] font-bold tracking-tight text-foreground">
        {agent.name}
      </h3>
      <p className="mt-1.5 text-[14px] leading-relaxed text-muted-foreground">
        {agent.summary}
      </p>

      <div className="mt-4 rounded-xl bg-muted/60 px-3 py-2.5">
        <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-muted-foreground">
          Use when
        </div>
        <p className="mt-0.5 text-[13px] leading-snug text-foreground/85">
          {agent.useWhen}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {agent.badges.map((b) => (
          <CapabilityBadge
            key={b}
            tone={badgeTone(b)}
            icon={
              b === 'Evidence required' ? (
                <EvidenceIcon width={12} height={12} />
              ) : undefined
            }
          >
            {b}
          </CapabilityBadge>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-1.5 pt-3 text-[13px] font-semibold text-primary">
        View agent
        <ArrowIcon
          width={15}
          height={15}
          className="transition-transform duration-200 group-hover:translate-x-0.5"
        />
      </div>
    </Link>
  )
}
