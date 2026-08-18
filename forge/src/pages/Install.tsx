import { useMemo, useState } from 'react'
import { Container, PageHeading } from '../components/Container'
import Breadcrumb from '../components/Breadcrumb'
import CommandBlock from '../components/CommandBlock'
import { CheckIcon } from '../components/Icons'
import { agents } from '../data/agents'

type Scope = 'entire' | 'selected'

const hosts = [
  { id: 'codex', name: 'Codex', enabled: true },
  { id: 'claude', name: 'Claude', enabled: false },
]

export default function Install() {
  const [host] = useState('codex')
  const [scope, setScope] = useState<Scope>('entire')
  const [selected, setSelected] = useState<string[]>([
    'principal-architect',
    'principal-engineer',
  ])

  const toggle = (slug: string) =>
    setSelected((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug],
    )

  const installCommand = useMemo(() => {
    const base = `agents install ${host}`
    if (scope === 'entire' || selected.length === 0) return base
    return base + ' ' + selected.map((s) => `--only ${s}`).join(' ')
  }, [host, scope, selected])

  return (
    <Container className="py-10">
      <Breadcrumb items={[{ label: 'Forge', to: '/' }, { label: 'Install' }]} />
      <div className="mt-5">
        <PageHeading
          eyebrow="Guided setup"
          title="Install 172X"
          description="Install the latest stable standalone CLI, then add selected Forge capabilities to Codex globally. Python is not required."
        />
      </div>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_400px]">
        {/* Builder */}
        <div className="space-y-8">
          <Step n={1} title="Host">
            <div className="grid gap-3 sm:grid-cols-2">
              {hosts.map((h) => (
                <OptionCard
                  key={h.id}
                  label={h.name}
                  selected={host === h.id && h.enabled}
                  disabled={!h.enabled}
                  badge={h.enabled ? undefined : 'Planned'}
                />
              ))}
            </div>
          </Step>

          <Step n={2} title="Scope">
            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                aria-pressed={scope === 'entire'}
                onClick={() => setScope('entire')}
                className={`rounded-xl border p-4 text-left transition-colors ${
                  scope === 'entire'
                    ? 'border-accent/50 bg-accent-soft'
                    : 'border-border-strong bg-card hover:border-primary/30'
                }`}
              >
                <span className="block text-[15px] font-semibold text-foreground">
                  Entire 172X library
                </span>
                <span className="mt-1 block text-[13px] text-muted-foreground">
                  Install every reviewed specialist and workflow.
                </span>
              </button>
              <button
                type="button"
                aria-pressed={scope === 'selected'}
                onClick={() => setScope('selected')}
                className={`rounded-xl border p-4 text-left transition-colors ${
                  scope === 'selected'
                    ? 'border-accent/50 bg-accent-soft'
                    : 'border-border-strong bg-card hover:border-primary/30'
                }`}
              >
                <span className="block text-[15px] font-semibold text-foreground">
                  Selected capabilities
                </span>
                <span className="mt-1 block text-[13px] text-muted-foreground">
                  Pick only the specialists this project needs.
                </span>
              </button>
            </div>

            {scope === 'selected' && (
              <div className="mt-4">
                <p className="mb-2 text-[13px] text-muted-foreground">
                  {selected.length} selected
                </p>
                <div className="flex flex-wrap gap-2">
                  {agents.map((a) => {
                    const on = selected.includes(a.slug)
                    return (
                      <button
                        key={a.slug}
                        type="button"
                        aria-pressed={on}
                        onClick={() => toggle(a.slug)}
                        className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[13px] font-medium transition-colors ${
                          on
                            ? 'border-primary bg-primary/8 text-primary'
                            : 'border-border-strong bg-card text-muted-foreground hover:border-primary/30'
                        }`}
                      >
                        {on && <CheckIcon width={13} height={13} />}
                        {a.name}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </Step>

          <Step n={3} title="Optional project activation">
            <div className="rounded-xl border border-border bg-muted/40 p-4 text-[13px] leading-relaxed text-muted-foreground">
              Forge installation is language-neutral. In a project, record expected gates without
              installing or modifying tools:
              <div className="mt-3">
                <CommandBlock command="agents activate python" compact />
              </div>
              <p className="mt-3">
                For a monorepo package, use{' '}
                <code className="font-mono text-foreground">--path services/api</code>.
              </p>
            </div>
          </Step>
        </div>

        {/* Command preview */}
        <aside>
          <div className="sticky top-24 space-y-5 rounded-[16px] border border-border bg-card p-5 shadow-[0_4px_20px_rgba(27,35,32,0.05)]">
            <h3 className="font-display text-[16px] font-bold tracking-tight text-foreground">
              Your commands
            </h3>
            <CommandBlock
              label="1 · Install the CLI (macOS/Linux)"
              command="curl -fsSL https://forge.172x.ai/install.sh | sh"
              compact
            />
            <CommandBlock
              label="1 · Install the CLI (Windows)"
              command="irm https://forge.172x.ai/install.ps1 | iex"
              compact
            />
            <CommandBlock label="2 · Install Forge" command={installCommand} compact />

            <div className="rounded-xl border border-border bg-muted/40 px-4 py-3 text-[13px] leading-relaxed text-muted-foreground">
              The installer downloads the latest stable 172X CLI by default; pass{' '}
              <span className="font-mono text-foreground">--version</span> to pin a release. Python
              is not required.{' '}
              <span className="font-mono text-foreground">agents install</span>{' '}
              adds selected Forge capabilities to Codex globally. Project activation is optional,
              local, and never installs external tools.
            </div>
          </div>
        </aside>
      </div>
    </Container>
  )
}

function Step({
  n,
  title,
  children,
}: {
  n: number
  title: string
  children: React.ReactNode
}) {
  return (
    <section>
      <div className="flex items-center gap-3">
        <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary font-mono text-[13px] font-semibold text-primary-foreground">
          {n}
        </span>
        <h2 className="font-display text-[18px] font-bold tracking-tight text-foreground">
          {title}
        </h2>
      </div>
      <div className="mt-4 pl-10">{children}</div>
    </section>
  )
}

function OptionCard({
  label,
  selected,
  disabled,
  badge,
}: {
  label: string
  selected: boolean
  disabled?: boolean
  badge?: string
}) {
  return (
    <div
      aria-disabled={disabled}
      className={`flex items-center justify-between rounded-xl border p-4 ${
        disabled
          ? 'cursor-not-allowed border-border bg-muted/40 opacity-70'
          : selected
            ? 'border-primary bg-primary/8'
            : 'border-border-strong bg-card'
      }`}
    >
      <span
        className={`text-[15px] font-semibold ${
          disabled ? 'text-muted-foreground' : 'text-foreground'
        }`}
      >
        {label}
      </span>
      {badge ? (
        <span className="rounded-full border border-accent/30 bg-accent-soft px-2 py-0.5 text-[11px] font-medium text-accent-foreground">
          {badge}
        </span>
      ) : selected ? (
        <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-primary text-primary-foreground">
          <CheckIcon width={13} height={13} />
        </span>
      ) : null}
    </div>
  )
}
