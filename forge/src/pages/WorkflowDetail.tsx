import { useParams, Link } from 'react-router'
import { Container } from '../components/Container'
import Breadcrumb from '../components/Breadcrumb'
import CommandBlock from '../components/CommandBlock'
import { domainIcon, ArrowIcon, GateIcon } from '../components/Icons'
import { workflowBySlug } from '../data/workflows'
import { agentBySlug } from '../data/agents'
import { catalogRevision } from '../data/catalog'
import NotFound from './NotFound'

export default function WorkflowDetail() {
  const { slug = '' } = useParams()
  const workflow = workflowBySlug[slug]
  if (!workflow) return <NotFound />

  const command = `agents install codex python --only ${workflow.slug}`
  const participants = workflow.agents
    .map((s) => agentBySlug[s])
    .filter(Boolean)

  return (
    <Container className="py-10">
      <Breadcrumb
        items={[
          { label: 'Forge', to: '/' },
          { label: 'Workflows', to: '/workflows' },
          { label: workflow.name },
        ]}
      />

      <div className="mt-6 max-w-3xl">
        <div className="font-mono text-[12px] uppercase tracking-[0.16em] text-accent">
          Workflow · v{workflow.version}
        </div>
        <h1 className="mt-2 font-display text-[clamp(1.9rem,4vw,2.6rem)] font-extrabold leading-tight tracking-tight text-foreground">
          {workflow.name}
        </h1>
        <p className="mt-3 text-[clamp(1.05rem,1.8vw,1.25rem)] font-medium leading-relaxed text-foreground/90">
          {workflow.outcome}
        </p>
        <p className="mt-3 text-[15px] leading-relaxed text-muted-foreground">
          {workflow.summary}
        </p>
      </div>

      {/* Flow diagram */}
      <section className="mt-10">
        <h2 className="font-display text-[13px] font-semibold uppercase tracking-[0.12em] text-accent">
          The flow
        </h2>
        <div className="mt-4 rounded-[16px] border border-border bg-card p-5 sm:p-6">
          <ol className="flex flex-wrap items-stretch gap-2">
            {workflow.steps.map((step, i) => {
              const isDecision = /decision|human/i.test(step)
              return (
                <li key={step} className="flex items-stretch gap-2">
                  <div
                    className={`flex min-w-[112px] flex-col justify-center rounded-xl border px-3.5 py-2.5 ${
                      isDecision
                        ? 'border-accent/40 bg-accent-soft'
                        : 'border-border bg-muted/50'
                    }`}
                  >
                    <span className="font-mono text-[10px] uppercase tracking-wide text-muted-foreground">
                      Step {i + 1}
                    </span>
                    <span
                      className={`mt-0.5 text-[13px] font-semibold leading-tight ${
                        isDecision ? 'text-accent-foreground' : 'text-foreground'
                      }`}
                    >
                      {step}
                    </span>
                  </div>
                  {i < workflow.steps.length - 1 && (
                    <span
                      aria-hidden
                      className="flex items-center text-border-strong"
                    >
                      →
                    </span>
                  )}
                </li>
              )
            })}
          </ol>
        </div>
      </section>

      <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_360px]">
        <div className="space-y-10">
          {/* Gates */}
          <section>
            <h2 className="flex items-center gap-2 font-display text-[13px] font-semibold uppercase tracking-[0.12em] text-accent">
              <GateIcon width={16} height={16} /> Feedback limits &amp; human gates
            </h2>
            <ul className="mt-4 space-y-3">
              {workflow.gates.map((g) => (
                <li
                  key={g}
                  className="rounded-xl border border-border bg-card px-4 py-3 text-[15px] leading-relaxed text-foreground/90"
                >
                  {g}
                </li>
              ))}
            </ul>
            <p className="mt-4 rounded-xl border border-primary/20 bg-primary/[0.04] px-4 py-3 text-[14px] leading-relaxed text-foreground/80">
              Workflows guide host-coordinated work. They sequence specialists
              and enforce gates — they are not a separate execution engine, and
              they never replace a human decision.
            </p>
          </section>

          {/* Participating agents */}
          <section>
            <h2 className="font-display text-[13px] font-semibold uppercase tracking-[0.12em] text-accent">
              Participating agents
            </h2>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {participants.map((a) => {
                const Icon = domainIcon[a.domain]
                return (
                  <Link
                    key={a.slug}
                    to={`/agents/${a.slug}`}
                    className="group flex items-center gap-3 rounded-xl border border-border bg-card p-3.5 transition-colors hover:border-primary/30"
                  >
                    <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-border bg-muted text-primary">
                      <Icon width={18} height={18} />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-[14px] font-semibold text-foreground">
                        {a.name}
                      </span>
                      <span className="block truncate text-[12px] capitalize text-muted-foreground">
                        {a.domain} · {a.kind}
                      </span>
                    </span>
                    <ArrowIcon
                      width={15}
                      height={15}
                      className="shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5"
                    />
                  </Link>
                )
              })}
            </div>
          </section>
        </div>

        {/* Install aside */}
        <aside>
          <div className="sticky top-24 rounded-[16px] border border-border bg-card p-5 shadow-[0_4px_20px_rgba(27,35,32,0.05)]">
            <h3 className="font-display text-[16px] font-bold tracking-tight text-foreground">
              Install {workflow.name}
            </h3>
            <p className="mt-1 text-[13px] leading-relaxed text-muted-foreground">
              Adds this workflow and its specialists to your project.
            </p>
            <div className="mt-4">
              <CommandBlock command={command} compact />
            </div>
            <Link
              to="/install"
              className="mt-4 inline-flex items-center gap-1.5 text-[13px] font-semibold text-primary hover:text-primary-hover"
            >
              Open the command builder
              <ArrowIcon width={14} height={14} />
            </Link>
            <p className="mt-4 border-t border-border pt-3 font-mono text-[11px] leading-relaxed text-muted-foreground">
              source: 172x-agents · v{workflow.version} · {catalogRevision}
            </p>
          </div>
        </aside>
      </div>
    </Container>
  )
}
