import type { Agent } from '../data/types'
import { catalogRevision } from '../data/catalog'
import { projectProfile } from '../data/compatibility'
import CommandBlock from './CommandBlock'
import { CheckIcon } from './Icons'

export default function InstallCard({ agent }: { agent: Agent }) {
  const command = `agents install codex python --only ${agent.slug}`

  return (
    <div className="rounded-[16px] border border-border bg-card p-5 shadow-[0_4px_20px_rgba(27,35,32,0.05)]">
      <h3 className="font-display text-[16px] font-bold tracking-tight text-foreground">
        Install {agent.name}
      </h3>
      <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">
        Adds this specialist to your current project profile.
      </p>

      <div className="mt-4">
        <CommandBlock command={command} compact />
      </div>

      <div className="mt-5">
        <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          Availability
        </div>
        <ul className="mt-2 space-y-1.5">
          <AvailabilityRow name="Codex" status="Available now" available />
          <AvailabilityRow name="Claude" status="Planned" />
        </ul>
      </div>

      <div className="mt-5 border-t border-border pt-4">
        <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          Project profile
        </div>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {projectProfile.map((p) => (
            <span
              key={p}
              className="rounded-md border border-border bg-muted/70 px-2 py-1 font-mono text-[12px] text-foreground/80"
            >
              {p}
            </span>
          ))}
        </div>
      </div>

      <p className="mt-4 border-t border-border pt-3 font-mono text-[11px] leading-relaxed text-muted-foreground">
        source: 172x-agents · {agent.domain} · v{agent.version} · {catalogRevision}
      </p>
    </div>
  )
}

function AvailabilityRow({
  name,
  status,
  available = false,
}: {
  name: string
  status: string
  available?: boolean
}) {
  return (
    <li className="flex items-center justify-between rounded-lg border border-border bg-muted/40 px-3 py-2">
      <span className="text-[13px] font-medium text-foreground">{name}</span>
      <span
        className={`inline-flex items-center gap-1.5 text-[12px] font-medium ${
          available ? 'text-primary' : 'text-muted-foreground'
        }`}
      >
        {available ? (
          <CheckIcon width={14} height={14} />
        ) : (
          <span
            aria-hidden
            className="h-1.5 w-1.5 rounded-full bg-accent/70"
          />
        )}
        {status}
      </span>
    </li>
  )
}
